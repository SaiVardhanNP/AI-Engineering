import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';

let apiPromise = null;
function loadYouTubeApi() {
  if (window.YT && window.YT.Player) return Promise.resolve(window.YT);
  if (apiPromise) return apiPromise;
  apiPromise = new Promise((resolve) => {
    const prevCallback = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      prevCallback?.();
      resolve(window.YT);
    };
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    document.head.appendChild(tag);
  });
  return apiPromise;
}

const YouTubePlayer = forwardRef(function YouTubePlayer(
  { videoId, onReady, onTimeUpdate, onPlayingChange },
  ref
) {
  const hostRef = useRef(null);
  const playerRef = useRef(null);
  const pollRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    loadYouTubeApi().then((YT) => {
      if (cancelled || !hostRef.current) return;

      playerRef.current = new YT.Player(hostRef.current, {
        videoId,
        playerVars: { rel: 0, modestbranding: 1 },
        events: {
          onReady: () => {
            if (cancelled) return;
            onReady?.(playerRef.current.getDuration());
          },
          onStateChange: (event) => {
            const playing = event.data === YT.PlayerState.PLAYING;
            onPlayingChange?.(playing);
            clearInterval(pollRef.current);
            if (playing) {
              pollRef.current = setInterval(() => {
                onTimeUpdate?.(playerRef.current.getCurrentTime());
              }, 250);
            }
          },
        },
      });
    });

    return () => {
      cancelled = true;
      clearInterval(pollRef.current);
      playerRef.current?.destroy?.();
      playerRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoId]);

  useImperativeHandle(ref, () => ({
    seekTo: (seconds) => playerRef.current?.seekTo(seconds, true),
    play: () => playerRef.current?.playVideo(),
    pause: () => playerRef.current?.pauseVideo(),
    getCurrentTime: () => playerRef.current?.getCurrentTime() ?? 0,
  }));

  return <div ref={hostRef} className="yt-frame-host" />;
});

export default YouTubePlayer;
