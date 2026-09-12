import { useState } from 'react';

export default function Composer({ draft, onDraftChange, onSend, disabled, placeholder }) {
  const [focused, setFocused] = useState(false);
  const canSend = !disabled && draft.trim().length > 0;

  return (
    <div className="flex-none border-t px-7" style={{ borderColor: 'var(--hairline-bar)', paddingTop: '15px', paddingBottom: '20px' }}>
      <div
        className={`field-underline${focused ? ' is-focused-neutral' : ''} flex items-center gap-3 pb-[9px]`}
        style={{ maxWidth: '640px' }}
      >
        <input
          type="text"
          value={draft}
          onChange={(e) => onDraftChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') onSend();
          }}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          disabled={disabled}
          placeholder={placeholder}
          aria-label="Ask about the transcript"
          className="flex-1 min-w-0 border-0 bg-transparent text-[16px] py-[5px] outline-none"
          style={{ color: 'var(--ink-bright)' }}
        />
        <button
          type="button"
          onClick={onSend}
          disabled={!canSend}
          className="text-[14px] font-medium px-0.5 py-1 border-0 bg-transparent"
          style={{
            color: canSend ? 'oklch(0.8 0.105 200)' : 'var(--ink-dim)',
            cursor: canSend ? 'pointer' : 'default',
            transition: 'color 180ms ease',
          }}
        >
          Ask
        </button>
      </div>
    </div>
  );
}
