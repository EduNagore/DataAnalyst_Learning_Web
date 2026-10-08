import { useId, useState } from 'react';
import { INTENTS, recommend, type Intent } from '../../lib/chartChooser';

/** Selector guiado: de la pregunta que quieres responder al gráfico recomendado. */
export default function ChartChooser() {
  const [intent, setIntent] = useState<Intent>('comparar');
  const [variantId, setVariantId] = useState('pocas');
  const groupId = useId();

  const info = INTENTS[intent];
  const rec = recommend(intent, variantId) ?? info.variants[0];

  const pick = (next: Intent) => {
    setIntent(next);
    setVariantId(INTENTS[next].variants[0].id);
  };

  const chip = (active: boolean) =>
    `rounded-md border px-3 py-1.5 text-sm text-left ${
      active
        ? 'border-[var(--color-accent)] bg-[var(--color-accent)] text-[var(--color-accent-contrast)]'
        : 'border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]'
    }`;

  return (
    <figure className="not-prose my-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4">
      <figcaption className="mb-3 text-sm font-semibold text-[var(--color-text)]">
        Elige el gráfico según la pregunta
      </figcaption>

      <div role="group" aria-labelledby={`${groupId}-q`}>
        <p
          id={`${groupId}-q`}
          className="mb-1 text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase"
        >
          1. ¿Qué quieres mostrar?
        </p>
        <div className="flex flex-wrap gap-2">
          {(Object.keys(INTENTS) as Intent[]).map((k) => (
            <button
              key={k}
              type="button"
              aria-pressed={intent === k}
              onClick={() => pick(k)}
              className={chip(intent === k)}
            >
              {INTENTS[k].label}
            </button>
          ))}
        </div>
      </div>

      <div role="group" aria-labelledby={`${groupId}-v`} className="mt-4">
        <p
          id={`${groupId}-v`}
          className="mb-1 text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase"
        >
          2. ¿En qué situación?
        </p>
        <div className="flex flex-wrap gap-2">
          {info.variants.map((v) => (
            <button
              key={v.id}
              type="button"
              aria-pressed={variantId === v.id}
              onClick={() => setVariantId(v.id)}
              className={chip(variantId === v.id)}
            >
              {v.when}
            </button>
          ))}
        </div>
      </div>

      <div
        role="status"
        aria-live="polite"
        className="mt-4 space-y-2 rounded-md border-l-4 border-[var(--color-accent)] bg-[var(--color-accent)]/10 p-3 text-sm"
      >
        <p className="text-xs text-[var(--color-text-muted)]">{info.question}</p>
        <p>
          <strong>Recomendado:</strong> {rec.chart}
        </p>
        <p>
          <strong>Por qué:</strong> {rec.why}
        </p>
        <p>
          <strong>Evita:</strong> {rec.avoid}
        </p>
      </div>
    </figure>
  );
}
