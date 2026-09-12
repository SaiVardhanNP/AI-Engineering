import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { extractVideoId, isYoutubeUrl } from '../lib/youtube';

const SAMPLE_URL = 'https://www.youtube.com/watch?v=ZHCB09O6zUk';

const BARS = [
  { width: 86, dur: 5.2, delay: 0 },
  { width: 64, dur: 4.4, delay: 0.3 },
  { width: 93, dur: 6.1, delay: 0.7 },
  { width: 71, dur: 4.9, delay: 1.1 },
  { width: 88, dur: 5.6, delay: 0.2 },
  { width: 57, dur: 4.2, delay: 0.9 },
  // cited row rendered separately
  { width: 79, dur: 5.4, delay: 0.5 },
  { width: 66, dur: 4.7, delay: 1.3 },
  { width: 91, dur: 5.9, delay: 0.4 },
  { width: 52, dur: 4.5, delay: 1.6 },
  { width: 84, dur: 6.3, delay: 0.8 },
  { width: 61, dur: 5.1, delay: 0.1 },
  { width: 75, dur: 4.8, delay: 1.4 },
];

const RAIL_LABELS = ['0:00', '06:10', '12:20', '14:02', '24:40', '30:50', '37:00'];

const TIMELINE_MARKS = [
  { pct: 9, delay: 1.17 },
  { pct: 23, delay: 2.99 },
  { pct: 48, delay: 6.24 },
  { pct: 66, delay: 8.58 },
  { pct: 87, delay: 11.31 },
];

export default function Landing() {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [focused, setFocused] = useState(false);
  const navigate = useNavigate();

  function load(raw) {
    const value = String(raw || '').trim();
    if (!value) {
      setError('Nothing to load yet — paste a link to a YouTube video and Marker will read its captions.');
      return;
    }
    if (!isYoutubeUrl(value)) {
      setError(
        'That is not a YouTube address. Marker reads captions from YouTube, so it needs a youtube.com or youtu.be link — a title or a channel name will not resolve to a video.'
      );
      return;
    }
    const videoId = extractVideoId(value);
    if (!videoId) {
      setError("Couldn't find a video ID in that link — check the URL and try again.");
      return;
    }
    navigate(`/watch/${videoId}`);
  }

  return (
    <div>
      <div
        className="max-w-[1180px] mx-auto px-[30px] pt-[34px] flex items-center justify-between gap-5"
        style={{ animation: 'fadeIn 700ms ease both' }}
      >
        <div className="mono text-xs" style={{ color: 'var(--ink-quiet)' }}>Marker</div>
        <div className="mono text-xs" style={{ color: 'var(--ink-dim)' }}>transcript-grounded</div>
      </div>

      <div className="max-w-[1180px] mx-auto px-[30px] pt-[60px] pb-24 flex gap-16 flex-wrap items-center min-h-[70vh]">
        <div className="flex-[1_1_440px] min-w-[290px] flex flex-col gap-[30px]">
          <h1
            className="m-0 font-medium max-w-[15em]"
            style={{
              fontSize: 'clamp(38px, 5.6vw, 64px)',
              lineHeight: 1.03,
              letterSpacing: '-0.03em',
              textWrap: 'pretty',
            }}
          >
            <span style={{ display: 'block', animation: 'riseIn 760ms cubic-bezier(0.2,0.7,0.25,1) 80ms both' }}>
              Ask a talk what it
            </span>
            <span style={{ display: 'block', animation: 'riseIn 760ms cubic-bezier(0.2,0.7,0.25,1) 200ms both' }}>
              actually said, and see
            </span>
            <span style={{ display: 'block', animation: 'riseIn 760ms cubic-bezier(0.2,0.7,0.25,1) 320ms both' }}>
              where it said it.
            </span>
          </h1>

          <p
            className="m-0 max-w-[33em]"
            style={{
              fontSize: '19px',
              lineHeight: 1.58,
              color: 'var(--ink-mid)',
              textWrap: 'pretty',
              animation: 'riseIn 760ms cubic-bezier(0.2,0.7,0.25,1) 460ms both',
            }}
          >
            Paste a YouTube link and Marker reads the transcript alongside you. Every answer carries the
            timestamp it came from, so a claim is one tap from the moment it was made — and that tap asks
            before it moves your playback.
          </p>

          <div
            className="flex flex-col gap-[14px] mt-0.5"
            style={{ animation: 'riseIn 760ms cubic-bezier(0.2,0.7,0.25,1) 600ms both' }}
          >
            <div
              className={`field-underline${focused ? ' is-focused' : ''} flex gap-[10px] items-center flex-wrap max-w-[560px] pb-[10px]`}
            >
              <input
                type="text"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  setError('');
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') load(url);
                }}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                placeholder="youtube.com/watch?v=…"
                aria-label="YouTube video URL"
                className="mono flex-[1_1_220px] min-w-0 border-0 bg-transparent text-[15px] py-2 px-0.5 outline-none"
                style={{ color: 'var(--ink-bright)' }}
              />
              <button
                type="button"
                onClick={() => load(url)}
                className="btn-outline-accent text-sm font-medium px-5 py-[9px]"
              >
                Load video
              </button>
            </div>

            {error ? (
              <div
                role="alert"
                className="max-w-[42em]"
                style={{
                  fontSize: '14.5px',
                  lineHeight: 1.55,
                  color: 'var(--ink-mid)',
                  animation: 'fadeIn 300ms ease both',
                }}
              >
                {error}
              </div>
            ) : (
              <div className="text-[14.5px]" style={{ color: 'var(--ink-faint)' }}>
                Reads any video with captions.{' '}
                <button
                  type="button"
                  onClick={() => {
                    setUrl(SAMPLE_URL);
                    load(SAMPLE_URL);
                  }}
                  className="text-link-accent"
                >
                  See it working on a sample talk
                </button>
              </div>
            )}
          </div>
        </div>

        <div
          className="flex-[1_1_400px] min-w-[280px] relative pt-1.5 pb-[54px]"
          style={{ animation: 'fadeIn 900ms ease 400ms both' }}
        >
          <div className="flex gap-[18px]">
            <div
              className="mono flex-none w-[42px] flex flex-col gap-[14px] text-right pt-px"
              style={{ fontSize: '10.5px', color: 'var(--ink-dim-2)' }}
            >
              {RAIL_LABELS.map((label, i) => (
                <div key={i} style={label === '14:02' ? { color: 'var(--accent)' } : undefined}>
                  {i > 0 && <div className="opacity-0">·</div>}
                  {label}
                </div>
              ))}
            </div>

            <div
              className="flex-1 flex flex-col gap-[14px] border-l pl-[22px]"
              style={{ borderColor: 'var(--hairline)' }}
            >
              {BARS.slice(0, 6).map((bar, i) => (
                <div
                  key={i}
                  className="h-2"
                  style={{
                    width: `${bar.width}%`,
                    background: 'var(--bar)',
                    transformOrigin: 'left',
                    animation: `breathe ${bar.dur}s ease-in-out ${bar.delay}s infinite`,
                  }}
                />
              ))}

              <div className="relative flex items-center gap-3">
                <div
                  className="h-2"
                  style={{
                    width: '44%',
                    background: 'var(--accent)',
                    transformOrigin: 'left',
                    animation: 'citedGlow 4.8s ease-in-out infinite',
                  }}
                />
                <div
                  className="mono text-xs font-medium px-[3px]"
                  style={{
                    color: 'var(--accent-bright)',
                    boxShadow: 'inset 0 -1px 0 0 var(--accent-50)',
                  }}
                >
                  14:02
                </div>
                <div
                  className="absolute pointer-events-none"
                  style={{
                    left: '44%',
                    top: '14px',
                    width: '1px',
                    height: '168px',
                    background: 'linear-gradient(to bottom, var(--accent), var(--accent-14))',
                    transformOrigin: 'top',
                    animation: 'threadDraw 4.8s cubic-bezier(0.3,0.7,0.3,1) infinite',
                  }}
                />
              </div>

              {BARS.slice(6).map((bar, i) => (
                <div
                  key={i}
                  className="h-2"
                  style={{
                    width: `${bar.width}%`,
                    background: 'var(--bar)',
                    transformOrigin: 'left',
                    animation: `breathe ${bar.dur}s ease-in-out ${bar.delay}s infinite`,
                  }}
                />
              ))}
            </div>
          </div>

          <div className="absolute h-[14px]" style={{ left: '82px', right: 0, bottom: '18px' }}>
            <div className="absolute left-0 right-0 top-[6px] h-px" style={{ background: 'var(--hairline)' }} />
            {TIMELINE_MARKS.map((mark, i) => (
              <div
                key={i}
                className="absolute top-px w-px h-[11px]"
                style={{
                  left: `${mark.pct}%`,
                  background: 'var(--mark)',
                  animation: `markLight 13s linear ${mark.delay}s infinite`,
                }}
              />
            ))}
            <div
              className="absolute top-0 w-px h-[13px]"
              style={{ left: '29%', background: 'var(--accent)', boxShadow: '0 0 8px var(--accent-60)' }}
            />
            <div
              className="absolute top-0 w-px h-[13px]"
              style={{ background: 'var(--ink-bright)', opacity: 0.8, animation: 'sweep 13s linear infinite' }}
            />
          </div>

          <div
            className="mono absolute"
            style={{ left: '82px', bottom: 0, fontSize: '10.5px', color: 'var(--ink-dim-2)' }}
          >
            transcript · 612 segments · 48:12
          </div>
        </div>
      </div>

      <div className="border-t" style={{ borderColor: 'var(--hairline-soft)' }}>
        <div className="max-w-[1180px] mx-auto px-[30px] pt-11 pb-[90px] flex gap-12 flex-wrap">
          <div className="flex-[1_1_240px] flex flex-col gap-[9px]">
            <div className="text-[16.5px] font-semibold" style={{ letterSpacing: '-0.012em' }}>
              Grounded in the transcript
            </div>
            <p className="m-0 text-[15px] leading-[1.62]" style={{ color: 'var(--ink-mid)' }}>
              Answers come from what was said in the video, not from a summary of it. If the talk never
              covers something, Marker says that instead of guessing.
            </p>
          </div>
          <div className="flex-[1_1_240px] flex flex-col gap-[9px]">
            <div className="text-[16.5px] font-semibold" style={{ letterSpacing: '-0.012em' }}>
              Citations you can check
            </div>
            <p className="m-0 text-[15px] leading-[1.62]" style={{ color: 'var(--ink-mid)' }}>
              Each claim ends in the timestamp behind it, set in the one color this interface uses for
              nothing else.
            </p>
          </div>
          <div className="flex-[1_1_240px] flex flex-col gap-[9px]">
            <div className="text-[16.5px] font-semibold" style={{ letterSpacing: '-0.012em' }}>
              Your playback stays yours
            </div>
            <p className="m-0 text-[15px] leading-[1.62]" style={{ color: 'var(--ink-mid)' }}>
              Tapping a citation asks first. Declining costs one keystroke and leaves the video exactly
              where it was.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
