import { shuffledOrder, type QuizQuestion } from '../../lib/quiz';
import InlineText from './InlineText';

/** Estado de respuesta de una pregunta en la UI (se convierte a QuizResponse al comprobar). */
export type UiAnswer = number | number[] | string | undefined;

export interface ClientQuestion extends QuizQuestion {
  moduleTitle?: string;
  lessonTitle?: string;
  module?: string;
  refUrl?: string;
}

interface Props {
  question: ClientQuestion;
  index: number;
  answer: UiAnswer;
  onChange: (value: UiAnswer) => void;
  disabled: boolean;
  seed: string;
}

const radioLike = new Set([
  'single',
  'truefalse',
  'sql-output',
  'formula-output',
  'chart-critique',
]);

export default function QuestionView({ question, index, answer, onChange, disabled, seed }: Props) {
  const options = question.options ?? [];
  // truefalse conserva su orden (Verdadero/Falso); el resto se baraja con semilla.
  const order =
    question.type === 'truefalse'
      ? options.map((_, i) => i)
      : shuffledOrder(options.length, `${question.id}:${seed}`);

  const name = `q-${question.id}`;
  const inputBase = 'mt-0.5 size-4 flex-none accent-[var(--color-accent)]';

  return (
    <fieldset className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4">
      <legend className="px-1 text-sm font-semibold text-[var(--color-text)]">
        {index + 1}. <InlineText text={question.prompt} />
      </legend>

      {question.code && (
        <pre className="mt-2 overflow-x-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3 font-mono text-xs text-[var(--color-text)]">
          <code>{question.code.replace(/\\n/g, '\n')}</code>
        </pre>
      )}
      {question.table && (
        <pre className="mt-2 overflow-x-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3 font-mono text-xs">
          {question.table}
        </pre>
      )}
      {question.image && (
        <img
          src={question.image}
          alt={question.imageAlt ?? ''}
          className="mt-2 max-w-full rounded-md border border-[var(--color-border)]"
        />
      )}

      {radioLike.has(question.type) && (
        <div className="mt-3 space-y-2">
          {order.map((origIdx) => (
            <label
              key={origIdx}
              className="flex items-start gap-2 text-sm text-[var(--color-text)]"
            >
              <input
                type="radio"
                name={name}
                className={inputBase}
                checked={answer === origIdx}
                disabled={disabled}
                onChange={() => onChange(origIdx)}
              />
              <span>
                <InlineText text={options[origIdx]} />
              </span>
            </label>
          ))}
        </div>
      )}

      {question.type === 'multiple' && (
        <div className="mt-3 space-y-2">
          <p className="text-xs text-[var(--color-text-muted)]">
            Hay más de una respuesta correcta.
          </p>
          {order.map((origIdx) => {
            const selected = Array.isArray(answer) ? answer : [];
            return (
              <label
                key={origIdx}
                className="flex items-start gap-2 text-sm text-[var(--color-text)]"
              >
                <input
                  type="checkbox"
                  className={inputBase}
                  checked={selected.includes(origIdx)}
                  disabled={disabled}
                  onChange={(e) =>
                    onChange(
                      e.target.checked
                        ? [...selected, origIdx].sort((a, b) => a - b)
                        : selected.filter((v) => v !== origIdx),
                    )
                  }
                />
                <span>
                  <InlineText text={options[origIdx]} />
                </span>
              </label>
            );
          })}
        </div>
      )}

      {question.type === 'order' && (
        <OrderInput
          options={options}
          order={order}
          chosen={Array.isArray(answer) ? answer : []}
          disabled={disabled}
          onChange={onChange}
        />
      )}

      {question.type === 'numeric' && (
        <div className="mt-3">
          <label className="text-xs text-[var(--color-text-muted)]" htmlFor={name}>
            Escribe un número (puedes usar coma decimal)
          </label>
          <input
            id={name}
            type="text"
            inputMode="decimal"
            autoComplete="off"
            className="mt-1 block w-40 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-sm text-[var(--color-text)]"
            value={typeof answer === 'string' ? answer : ''}
            disabled={disabled}
            onChange={(e) => onChange(e.target.value)}
          />
        </div>
      )}
    </fieldset>
  );
}

function OrderInput({
  options,
  order,
  chosen,
  disabled,
  onChange,
}: {
  options: string[];
  order: number[];
  chosen: number[];
  disabled: boolean;
  onChange: (v: UiAnswer) => void;
}) {
  const remaining = order.filter((i) => !chosen.includes(i));
  return (
    <div className="mt-3 space-y-3">
      <p className="text-xs text-[var(--color-text-muted)]">
        Pulsa las opciones en el orden correcto (la primera pulsada será la primera).
      </p>
      <ol className="list-inside list-decimal space-y-1 text-sm text-[var(--color-text)]">
        {chosen.map((i) => (
          <li key={i}>
            <InlineText text={options[i]} />
          </li>
        ))}
        {chosen.length === 0 && (
          <li className="list-none text-[var(--color-text-muted)]">Aún no has elegido ninguna.</li>
        )}
      </ol>
      <div className="flex flex-wrap gap-2">
        {remaining.map((i) => (
          <button
            key={i}
            type="button"
            disabled={disabled}
            onClick={() => onChange([...chosen, i])}
            className="rounded-md border border-[var(--color-border)] px-3 py-1 text-sm text-[var(--color-text)] hover:border-[var(--color-accent)] disabled:opacity-50"
          >
            <InlineText text={options[i]} />
          </button>
        ))}
        {chosen.length > 0 && (
          <button
            type="button"
            disabled={disabled}
            onClick={() => onChange([])}
            className="rounded-md px-3 py-1 text-sm text-[var(--color-accent)] hover:underline disabled:opacity-50"
          >
            Reiniciar orden
          </button>
        )}
      </div>
    </div>
  );
}
