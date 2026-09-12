import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ingestVideo, askQuestion } from '../api';
import { fetchVideoMeta, formatTime, parseTimeToSeconds } from '../lib/youtube';
import { prefersReducedMotion } from '../lib/dom';
import YouTubePlayer from '../components/YouTubePlayer';
import Scrubber from '../components/Scrubber';
import ChatMessage from '../components/ChatMessage';
import Composer from '../components/Composer';

export default function Watch() {
  const { videoId } = useParams();
  const navigate = useNavigate();

  const [phase, setPhase] = useState('indexing'); // indexing | ready | failed
  const [errorMessage, setErrorMessage] = useState('');
  const [meta, setMeta] = useState(null);

  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [playing, setPlaying] = useState(false);

  const [messages, setMessages] = useState([]);
  const [thinking, setThinking] = useState(false);
  const [draft, setDraft] = useState('');
  const [newMessageIndex, setNewMessageIndex] = useState(-1);
  const [openCitationKey, setOpenCitationKey] = useState(null);

  const [ratio, setRatio] = useState(0.58);
  const [width, setWidth] = useState(window.innerWidth);
  const wide = width >= 860;

  const playerRef = useRef(null);
  const glidingRef = useRef(false);
  const rafRef = useRef(null);
  const animTimeoutRef = useRef(null);
  const streamRef = useRef(null);

  // ingest + fetch metadata for this video (component is remounted, via a
  // `key={videoId}` in App.jsx, whenever the route's videoId changes -
  // so state here always starts fresh and never needs manual resetting)
  useEffect(() => {
    let cancelled = false;

    ingestVideo(videoId)
      .then(() => {
        if (!cancelled) setPhase('ready');
      })
      .catch((err) => {
        if (!cancelled) {
          setPhase('failed');
          setErrorMessage(err.message);
        }
      });

    fetchVideoMeta(videoId).then((result) => {
      if (!cancelled && result) setMeta(result);
    });

    return () => {
      cancelled = true;
    };
  }, [videoId]);

  useEffect(() => {
    const onResize = () => setWidth(window.innerWidth);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape' && openCitationKey) setOpenCitationKey(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [openCitationKey]);

  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [messages, thinking]);

  useEffect(
    () => () => {
      clearTimeout(animTimeoutRef.current);
      cancelAnimationFrame(rafRef.current);
    },
    []
  );

  const glideTo = useCallback(
    (target) => {
      setOpenCitationKey(null);
      const from = currentTime;

      if (prefersReducedMotion() || Math.abs(target - from) < 2) {
        playerRef.current?.seekTo(target);
        playerRef.current?.play();
        setCurrentTime(target);
        return;
      }

      glidingRef.current = true;
      playerRef.current?.seekTo(target);
      playerRef.current?.play();

      const start = performance.now();
      const dur = 520;
      const step = (now) => {
        const p = Math.min(1, (now - start) / dur);
        const eased = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
        setCurrentTime(from + (target - from) * eased);
        if (p < 1) {
          rafRef.current = requestAnimationFrame(step);
        } else {
          glidingRef.current = false;
        }
      };
      rafRef.current = requestAnimationFrame(step);
    },
    [currentTime]
  );

  async function handleSend() {
    const question = draft.trim();
    if (!question || thinking || phase !== 'ready') return;

    setMessages((prev) => {
      const next = [...prev, { role: 'user', text: question }];
      setNewMessageIndex(next.length - 1);
      return next;
    });
    setDraft('');
    setThinking(true);
    setOpenCitationKey(null);
    clearTimeout(animTimeoutRef.current);
    animTimeoutRef.current = setTimeout(() => setNewMessageIndex(-1), 700);

    try {
      const result = await askQuestion(videoId, question, 3);
      setMessages((prev) => {
        const next = [...prev, { role: 'assistant', text: result.answer, sources: result.sources }];
        setNewMessageIndex(next.length - 1);
        return next;
      });
    } catch (err) {
      setMessages((prev) => {
        const next = [...prev, { role: 'assistant', text: err.message, sources: [] }];
        setNewMessageIndex(next.length - 1);
        return next;
      });
    } finally {
      setThinking(false);
      clearTimeout(animTimeoutRef.current);
      animTimeoutRef.current = setTimeout(() => setNewMessageIndex(-1), 800);
    }
  }

  function startDrag(e) {
    e.preventDefault();
    const move = (ev) => setRatio(Math.min(0.72, Math.max(0.38, ev.clientX / window.innerWidth)));
    const up = () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
    };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
  }

  const citations = messages.flatMap((m, i) =>
    (m.sources || []).map((s, j) => ({ key: `${i}:${j}`, seconds: parseTimeToSeconds(s.start) }))
  );
  const ticks = citations.map((c) => c.seconds);
  const openTickSeconds = citations.find((c) => c.key === openCitationKey)?.seconds;

  const phaseNote =
    phase === 'ready'
      ? formatTime(duration) === '0:00'
        ? 'ready'
        : `${citations.length ? citations.length + ' cited · ' : ''}${formatTime(duration)}`
      : phase === 'failed'
      ? 'no captions'
      : 'reading captions';

  return (
    <div className="flex flex-col min-h-screen" style={{ animation: 'fadeIn 500ms ease both' }}>
      <div
        className="flex-none h-12 flex items-center justify-between gap-4 px-[22px] border-b"
        style={{ borderColor: 'var(--hairline)' }}
      >
        <div className="flex items-baseline gap-3.5 min-w-0">
          <div className="mono text-xs whitespace-nowrap" style={{ color: 'var(--ink-quiet)' }}>
            Marker
          </div>
          <div
            className="mono text-[11.5px] whitespace-nowrap overflow-hidden text-ellipsis"
            style={{ color: 'var(--ink-dim)' }}
          >
            {phaseNote}
          </div>
        </div>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="text-[13.5px] border-0 bg-transparent py-1 whitespace-nowrap flex-none"
          style={{ color: 'var(--ink-mid)', boxShadow: 'inset 0 -1px 0 0 var(--control-border)' }}
        >
          New video
        </button>
      </div>

      <div className={wide ? 'flex items-stretch' : 'flex flex-col'} style={wide ? { height: 'calc(100vh - 48px)' } : { minHeight: 'calc(100vh - 48px)' }}>
        <div
          className={wide ? 'flex justify-center items-start overflow-y-auto p-9' : 'sticky top-0 z-[6] flex justify-center px-5 pt-4 pb-3.5 border-b'}
          style={
            wide
              ? { flex: `0 0 ${ratio * 100}%`, minWidth: 0 }
              : { background: 'var(--ground)', borderColor: 'var(--hairline-bar)' }
          }
        >
          <div className="w-full max-w-[820px] flex flex-col gap-5">
            <div
              className="relative w-full overflow-hidden border"
              style={{
                aspectRatio: wide ? '16 / 9' : '16 / 10',
                maxHeight: wide ? 'none' : '31vh',
                background:
                  'repeating-linear-gradient(135deg, var(--frame-a) 0 9px, var(--frame-b) 9px 18px)',
                borderColor: 'var(--hairline)',
              }}
            >
              {phase === 'indexing' && (
                <div className="absolute inset-0 overflow-hidden">
                  <div
                    className="absolute left-0 right-0"
                    style={{
                      height: '34%',
                      background:
                        'linear-gradient(to bottom, transparent, var(--accent-09), transparent)',
                      animation: 'frameSheen 2.6s cubic-bezier(0.4,0,0.6,1) infinite',
                    }}
                  />
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
                    <div className="flex items-end gap-[5px] h-[22px]">
                      {[
                        [10, 0],
                        [18, 0.14],
                        [13, 0.28],
                        [21, 0.42],
                        [15, 0.56],
                      ].map(([h, d], i) => (
                        <div
                          key={i}
                          style={{
                            width: '3px',
                            height: `${h}px`,
                            background: 'var(--accent)',
                            animation: `scanBar 1.3s ease-in-out ${d}s infinite`,
                          }}
                        />
                      ))}
                    </div>
                    <div className="mono text-xs" style={{ color: 'var(--ink-faint)' }}>
                      fetching transcript
                    </div>
                  </div>
                </div>
              )}

              {phase === 'ready' && (
                <YouTubePlayer
                  ref={playerRef}
                  videoId={videoId}
                  onReady={(d) => setDuration(d)}
                  onTimeUpdate={(t) => {
                    if (!glidingRef.current) setCurrentTime(t);
                  }}
                  onPlayingChange={setPlaying}
                />
              )}
            </div>

            <div className="flex flex-col gap-[13px]">
              <div className="flex items-baseline justify-between gap-[18px] flex-wrap">
                <div
                  className="text-[17.5px] font-semibold max-w-[30em]"
                  style={{ letterSpacing: '-0.014em' }}
                >
                  {meta?.title || `Video ${videoId}`}
                </div>
                <div className="mono text-xs" style={{ color: 'var(--ink-fainter)' }}>
                  {meta?.channel || ''}
                </div>
              </div>

              <Scrubber
                duration={duration}
                currentTime={currentTime}
                ticks={ticks}
                openTickSeconds={openTickSeconds}
                onScrub={(seconds) => {
                  playerRef.current?.seekTo(seconds);
                  setCurrentTime(seconds);
                }}
              />

              <div className="flex items-center gap-[18px] flex-wrap">
                <button
                  type="button"
                  onClick={() => (playing ? playerRef.current?.pause() : playerRef.current?.play())}
                  disabled={phase !== 'ready'}
                  className="btn-outline mono text-xs px-[13px] py-1.5"
                >
                  {playing ? 'pause' : 'play'}
                </button>
                <div className="mono text-[12.5px]" style={{ color: 'var(--ink-mid)' }}>
                  {formatTime(currentTime)} / {formatTime(duration)}
                </div>
                {phase === 'ready' && citations.length > 0 && (
                  <div className="mono text-[11.5px]" style={{ color: 'var(--ink-fainter-2)' }}>
                    {citations.length} cited moment{citations.length === 1 ? '' : 's'}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {wide && (
          <div
            role="separator"
            tabIndex={0}
            aria-label="Resize panes"
            onMouseDown={startDrag}
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft') setRatio((r) => Math.max(0.38, r - 0.02));
              if (e.key === 'ArrowRight') setRatio((r) => Math.min(0.72, r + 0.02));
            }}
            className="flex-none w-[11px] flex justify-center"
            style={{ cursor: 'col-resize' }}
          >
            <div className="w-px" style={{ background: 'var(--hairline)' }} />
          </div>
        )}

        <div
          className={wide ? 'flex flex-col' : 'flex flex-col flex-1'}
          style={{ flex: wide ? '1 1 0' : undefined, minWidth: 0, background: 'var(--pane-chat)' }}
        >
          <div
            ref={streamRef}
            className={wide ? 'overflow-y-auto flex justify-start' : 'flex'}
            style={{ flex: wide ? '1 1 0' : '1 1 auto', minHeight: 0 }}
          >
            <div className="max-w-[640px] w-full flex flex-col gap-[34px] px-7 pt-8 pb-3">
              {phase === 'failed' && (
                <div
                  className="flex flex-col gap-[15px] items-start"
                  style={{ animation: 'riseIn 500ms ease both' }}
                >
                  <div className="mono text-[11.5px]" style={{ color: 'var(--ink-faint)' }}>
                    transcript unavailable
                  </div>
                  <p className="m-0 text-[16.5px] leading-[1.62] max-w-[30em]" style={{ textWrap: 'pretty' }}>
                    {errorMessage ||
                      'This video has captions disabled, so there is nothing for Marker to read.'}
                  </p>
                  <button type="button" onClick={() => navigate('/')} className="btn-outline text-sm px-[17px] py-2">
                    Try another link
                  </button>
                </div>
              )}

              {phase === 'indexing' && (
                <div className="flex flex-col gap-[11px]" style={{ animation: 'fadeIn 400ms ease both' }}>
                  <div className="mono text-[11.5px]" style={{ color: 'var(--ink-faint)' }}>
                    one moment
                  </div>
                  <p
                    className="m-0 text-[16.5px] leading-[1.62] max-w-[28em]"
                    style={{ color: 'var(--ink-mid)' }}
                  >
                    Marker is reading the captions end to end. Questions open up as soon as that finishes.
                  </p>
                </div>
              )}

              {messages.map((message, i) => (
                <ChatMessage
                  key={i}
                  msgIndex={i}
                  message={message}
                  isNew={i === newMessageIndex}
                  currentTime={currentTime}
                  openCitationKey={openCitationKey}
                  onOpenCitation={setOpenCitationKey}
                  onCloseCitation={() => setOpenCitationKey(null)}
                  onConfirmCitation={glideTo}
                />
              ))}

              {thinking && (
                <div className="flex flex-col gap-3" style={{ animation: 'fadeIn 320ms ease both' }}>
                  <div className="mono text-[11.5px]" style={{ color: 'var(--ink-fainter)' }}>
                    Marker
                  </div>
                  <div className="relative flex flex-col gap-[9px] max-w-[300px] overflow-hidden py-0.5">
                    <div className="h-[7px]" style={{ width: '82%', background: 'var(--hairline-bar)' }} />
                    <div className="h-[7px]" style={{ width: '96%', background: 'var(--hairline-bar)' }} />
                    <div className="h-[7px]" style={{ width: '68%', background: 'var(--hairline-bar)' }} />
                    <div
                      className="absolute inset-0"
                      style={{
                        background:
                          'linear-gradient(90deg, transparent, var(--accent-50), transparent)',
                        animation: 'scanLine 1.9s cubic-bezier(0.4,0,0.6,1) infinite',
                        mixBlendMode: 'screen',
                      }}
                    />
                  </div>
                  <div className="text-[14.5px]" style={{ color: 'var(--ink-mid)' }}>
                    Reading the relevant stretch of transcript
                  </div>
                </div>
              )}
            </div>
          </div>

          <Composer
            draft={draft}
            onDraftChange={setDraft}
            onSend={handleSend}
            disabled={phase !== 'ready'}
            placeholder={phase === 'ready' ? 'Ask about anything in the talk' : 'Waiting on the transcript'}
          />
        </div>
      </div>
    </div>
  );
}
