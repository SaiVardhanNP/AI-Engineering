function seek(e, duration, onScrub) {
  if (!duration) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
  onScrub(ratio * duration);
}

export default function Scrubber({ duration, currentTime, ticks, openTickSeconds, onScrub }) {
  const pct = duration ? (currentTime / duration) * 100 : 0;

  return (
    <div
      role="slider"
      tabIndex={0}
      aria-label="Video position"
      onClick={(e) => seek(e, duration, onScrub)}
      className="relative h-6 flex items-center cursor-pointer"
    >
      <div className="absolute left-0 right-0 h-[2px]" style={{ background: 'var(--hairline)' }} />

      <div
        className="absolute left-0 h-[2px]"
        style={{
          width: `${pct}%`,
          background: 'linear-gradient(90deg, var(--progress-start), var(--accent))',
        }}
      />

      {ticks.map((t, i) => {
        const near = Math.abs(t - currentTime) < 3;
        const open = openTickSeconds === t;
        return (
          <div
            key={i}
            className="absolute w-px"
            style={{
              left: `${(t / duration) * 100}%`,
              height: open ? '18px' : near ? '15px' : '10px',
              background: 'var(--accent)',
              opacity: open || near ? 1 : 0.6,
              boxShadow: open || near ? '0 0 12px var(--accent-85)' : 'none',
              transition:
                'height 220ms cubic-bezier(0.2, 0.7, 0.25, 1), opacity 220ms ease, box-shadow 220ms ease',
            }}
          />
        );
      })}

      <div
        className="absolute w-[2px] h-[14px]"
        style={{
          left: `calc(${pct}% - 1px)`,
          background: 'var(--ink-bright)',
          boxShadow: '0 0 10px oklch(0.9 0.02 262 / 0.6)',
        }}
      />
    </div>
  );
}
