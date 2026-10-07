import { Fragment } from 'react';

/** Renderiza texto con `código en línea` (entre backticks) y saltos de línea. */
export default function InlineText({ text }: { text: string }) {
  const parts = text.split(/(`[^`]+`)/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith('`') && part.endsWith('`') && part.length > 2 ? (
          <code
            key={i}
            className="rounded bg-[var(--color-bg-subtle)] px-1 py-0.5 font-mono text-[0.9em]"
          >
            {part.slice(1, -1)}
          </code>
        ) : (
          <Fragment key={i}>{part}</Fragment>
        ),
      )}
    </>
  );
}
