import type { CheckItem } from '../../lib/lab/sqlCheck';
import InlineText from '../quiz/InlineText';

/** Lista de comprobaciones (✔/✘) con mensajes didácticos. Los tests ocultos muestran solo el resultado. */
export default function TestResults({ items }: { items: CheckItem[] }) {
  return (
    <ul className="space-y-2" aria-live="polite">
      {items.map((item) => (
        <li
          key={item.name}
          className={
            'rounded-md border-l-4 p-3 text-sm ' +
            (item.passed
              ? 'border-[var(--color-success)] bg-[var(--color-success)]/10'
              : 'border-[var(--color-danger)] bg-[var(--color-danger)]/10')
          }
        >
          <p className="font-semibold text-[var(--color-text)]">
            <span aria-hidden="true">{item.passed ? '✔ ' : '✘ '}</span>
            {item.name}
            <span className="sr-only">{item.passed ? ' — superado' : ' — no superado'}</span>
          </p>
          <p className="mt-1 whitespace-pre-wrap text-[var(--color-text)]">
            <InlineText text={item.message} />
          </p>
        </li>
      ))}
    </ul>
  );
}
