import { useLayoutEffect, useRef, useState } from 'react';
import { formatTime } from '../lib/youtube';
import { scrollParent } from '../lib/dom';

const POP_W = 272;

export default function Citation({ seconds, currentTime, isOpen, onOpen, onClose, onConfirm }) {
  const btnRef = useRef(null);
  const [placement, setPlacement] = useState({ shift: 0, below: false });

  useLayoutEffect(() => {
    if (!isOpen || !btnRef.current) return;

    const rect = btnRef.current.getBoundingClientRect();
    const container = scrollParent(btnRef.current);
    const bounds = container ? container.getBoundingClientRect() : null;
    const minX = (bounds ? bounds.left : 0) + 14;
    const maxX = (bounds ? bounds.right : window.innerWidth) - POP_W - 14;
    const wantX = rect.left + rect.width / 2 - POP_W / 2;
    const clampedX = Math.max(minX, Math.min(maxX, wantX));
    const topRoom = rect.top - (bounds ? bounds.top : 0);

    setPlacement({ shift: Math.round(clampedX - wantX), below: topRoom < 185 });
  }, [isOpen]);

  const label = formatTime(seconds);
  const sub =
    seconds > currentTime
      ? `That is ${formatTime(seconds - currentTime)} ahead of where you are now (${formatTime(currentTime)}).`
      : `You are at ${formatTime(currentTime)} — this moves you back.`;

  return (
    <span className="relative whitespace-nowrap">
      <button
        ref={btnRef}
        type="button"
        onClick={() => (isOpen ? onClose() : onOpen())}
        aria-label={`Citation at ${label}, opens a jump confirmation`}
        className={`citation-btn${isOpen ? ' is-open' : ''}`}
      >
        {label}
      </button>

      {isOpen && (
        <span
          className="absolute z-20 block"
          style={{
            left: '50%',
            width: `${POP_W}px`,
            bottom: placement.below ? 'auto' : 'calc(100% + 13px)',
            top: placement.below ? 'calc(100% + 13px)' : 'auto',
            transform: `translateX(${-POP_W / 2 + placement.shift}px)`,
          }}
        >
          <span
            role="dialog"
            aria-label="Confirm jump"
            className={`popover-card ${placement.below ? 'below' : 'above'}`}
          >
            <span className="flex flex-col gap-1.5">
              <span
                className="text-[15.5px] font-semibold"
                style={{ letterSpacing: '-0.01em', color: 'var(--ink-bright)' }}
              >
                Jump to {label}?
              </span>
              <span className="text-[13.5px] leading-[1.5]" style={{ color: 'var(--ink-mid)' }}>
                {sub}
              </span>
            </span>
            <span className="flex gap-[9px]">
              <button
                type="button"
                onClick={onConfirm}
                className="btn-solid-accent text-[13.5px] font-semibold px-[15px] py-2"
              >
                Jump
              </button>
              <button
                type="button"
                onClick={onClose}
                className="btn-quiet text-[13.5px] font-medium px-[15px] py-2"
              >
                Stay here
              </button>
            </span>
          </span>
        </span>
      )}
    </span>
  );
}
