import Citation from './Citation';
import { parseTimeToSeconds } from '../lib/youtube';

export default function ChatMessage({
  message,
  isNew,
  currentTime,
  openCitationKey,
  onOpenCitation,
  onCloseCitation,
  onConfirmCitation,
  msgIndex,
}) {
  const isUser = message.role === 'user';

  return (
    <div
      className={isNew ? 'flex flex-col' : 'flex flex-col'}
      style={{
        gap: isUser ? '7px' : '10px',
        borderLeft: isUser ? '1px solid var(--line-strong)' : 'none',
        paddingLeft: isUser ? '17px' : '0',
        animation: isNew ? 'msgIn 420ms cubic-bezier(0.2, 0.7, 0.25, 1) both' : 'none',
      }}
    >
      <div
        className="mono text-[11.5px]"
        style={{ color: 'var(--ink-fainter)', letterSpacing: '0.01em' }}
      >
        {isUser ? 'You' : 'Marker'}
      </div>

      {isUser ? (
        <div
          className="text-[16.5px] leading-[1.62] font-medium"
          style={{ color: 'var(--ink-user)' }}
        >
          {message.text}
        </div>
      ) : (
        <>
          <div
            className="text-[16.5px] leading-[1.74]"
            style={{ color: 'var(--ink-body)', textWrap: 'pretty' }}
          >
            {message.text}
          </div>

          {message.sources?.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 mt-1">
              <span className="mono text-[11.5px]" style={{ color: 'var(--ink-fainter-2)' }}>
                sources
              </span>
              {message.sources.map((source, i) => {
                const key = `${msgIndex}:${i}`;
                const seconds = parseTimeToSeconds(source.start);
                return (
                  <Citation
                    key={key}
                    seconds={seconds}
                    currentTime={currentTime}
                    isOpen={openCitationKey === key}
                    onOpen={() => onOpenCitation(key)}
                    onClose={onCloseCitation}
                    onConfirm={() => onConfirmCitation(seconds)}
                  />
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
