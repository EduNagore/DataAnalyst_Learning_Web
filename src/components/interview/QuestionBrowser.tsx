import { useEffect, useMemo, useState } from 'react';

export interface InterviewQuestion {
  id: string;
  topic: string;
  level: 'junior' | 'mid' | 'senior';
  type: 'conceptual' | 'design' | 'debugging';
  promptEs: string;
  promptEn: string;
  answerEs: string;
  answerEn: string;
}

type Lang = 'es' | 'en';
type Mode = 'lista' | 'flashcards';
type Mark = 'known' | 'review';

const STORAGE_KEY = 'daa:interview:v1';

const LEVEL_LABEL: Record<Lang, Record<string, string>> = {
  es: { all: 'Todos los niveles', junior: 'Junior', mid: 'Intermedio', senior: 'Sénior' },
  en: { all: 'All levels', junior: 'Junior', mid: 'Mid', senior: 'Senior' },
};
const TYPE_LABEL: Record<Lang, Record<string, string>> = {
  es: {
    all: 'Todos los tipos',
    conceptual: 'Conceptual',
    design: 'Diseño',
    debugging: 'Depuración',
  },
  en: { all: 'All types', conceptual: 'Conceptual', design: 'Design', debugging: 'Debugging' },
};

const T = {
  es: {
    topic: 'Tema',
    search: 'Buscar en las preguntas…',
    show: 'Mostrar respuesta',
    hide: 'Ocultar respuesta',
    count: (n: number, t: number) => `${n} de ${t} preguntas`,
    list: 'Lista',
    cards: 'Flashcards',
    allTopics: 'Todos los temas',
    known: 'La sabía',
    review: 'Repasar',
    next: 'Siguiente',
    reset: 'Reiniciar marcas',
    none: 'Ninguna pregunta coincide con los filtros.',
    progress: (k: number, r: number) => `Marcadas: ${k} sabidas · ${r} para repasar`,
    answer: 'Respuesta modelo',
    shuffle: 'Barajar',
    cardOf: (i: number, n: number) => `Tarjeta ${i} de ${n}`,
  },
  en: {
    topic: 'Topic',
    search: 'Search questions…',
    show: 'Show answer',
    hide: 'Hide answer',
    count: (n: number, t: number) => `${n} of ${t} questions`,
    list: 'List',
    cards: 'Flashcards',
    allTopics: 'All topics',
    known: 'I knew it',
    review: 'Review',
    next: 'Next',
    reset: 'Reset marks',
    none: 'No question matches the filters.',
    progress: (k: number, r: number) => `Marked: ${k} known · ${r} to review`,
    answer: 'Model answer',
    shuffle: 'Shuffle',
    cardOf: (i: number, n: number) => `Card ${i} of ${n}`,
  },
};

function loadMarks(): Record<string, Mark> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Record<string, Mark>) : {};
  } catch {
    return {};
  }
}

function saveMarks(marks: Record<string, Mark>) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(marks));
  } catch {
    /* sin almacenamiento: la funcionalidad sigue sin persistir */
  }
}

function shuffled<T>(items: T[]): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

const selectClass =
  'rounded-md border border-[var(--color-border)] bg-[var(--color-bg-raised)] px-2 py-1.5 text-sm text-[var(--color-text)]';
const buttonClass =
  'rounded-md border border-[var(--color-border)] bg-[var(--color-bg-raised)] px-3 py-1.5 text-sm text-[var(--color-text)] hover:border-[var(--color-accent)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-accent)]';

export default function QuestionBrowser({ questions }: { questions: InterviewQuestion[] }) {
  const [lang, setLang] = useState<Lang>('es');
  const [mode, setMode] = useState<Mode>('lista');
  const [topic, setTopic] = useState('all');
  const [level, setLevel] = useState('all');
  const [type, setType] = useState('all');
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState<Set<string>>(new Set());
  const [marks, setMarks] = useState<Record<string, Mark>>({});
  const [order, setOrder] = useState<string[]>(() => questions.map((q) => q.id));
  const [cursor, setCursor] = useState(0);

  useEffect(() => setMarks(loadMarks()), []);

  const t = T[lang];
  const topics = useMemo(() => [...new Set(questions.map((q) => q.topic))], [questions]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return questions.filter((q) => {
      if (topic !== 'all' && q.topic !== topic) return false;
      if (level !== 'all' && q.level !== level) return false;
      if (type !== 'all' && q.type !== type) return false;
      if (!needle) return true;
      const text = (
        lang === 'es' ? q.promptEs + q.answerEs : q.promptEn + q.answerEn
      ).toLowerCase();
      return text.includes(needle);
    });
  }, [questions, topic, level, type, query, lang]);

  const cards = useMemo(() => {
    const byId = new Map(filtered.map((q) => [q.id, q]));
    return order.map((id) => byId.get(id)).filter((q): q is InterviewQuestion => Boolean(q));
  }, [filtered, order]);

  useEffect(() => setCursor(0), [topic, level, type, query]);

  const toggle = (id: string) =>
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const mark = (id: string, m: Mark) => {
    const next = { ...marks, [id]: m };
    setMarks(next);
    saveMarks(next);
  };

  const known = Object.values(marks).filter((m) => m === 'known').length;
  const review = Object.values(marks).filter((m) => m === 'review').length;
  const card = cards[Math.min(cursor, Math.max(cards.length - 1, 0))];
  const cardOpen = card ? open.has(card.id) : false;

  const prompt = (q: InterviewQuestion) => (lang === 'es' ? q.promptEs : q.promptEn);
  const answer = (q: InterviewQuestion) => (lang === 'es' ? q.answerEs : q.answerEn);

  const next = () => {
    if (card) setOpen((prev) => new Set([...prev].filter((x) => x !== card.id)));
    setCursor((c) => (cards.length ? (c + 1) % cards.length : 0));
  };

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Filtros">
        <div
          className="inline-flex overflow-hidden rounded-md border border-[var(--color-border)]"
          role="group"
          aria-label="Idioma"
        >
          {(['es', 'en'] as Lang[]).map((l) => (
            <button
              key={l}
              type="button"
              aria-pressed={lang === l}
              onClick={() => setLang(l)}
              className={`px-3 py-1.5 text-sm ${lang === l ? 'bg-[var(--color-accent)] text-[var(--color-accent-contrast)]' : 'bg-[var(--color-bg-raised)] text-[var(--color-text)]'}`}
            >
              {l.toUpperCase()}
            </button>
          ))}
        </div>
        <div
          className="inline-flex overflow-hidden rounded-md border border-[var(--color-border)]"
          role="group"
          aria-label="Modo"
        >
          {(['lista', 'flashcards'] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              aria-pressed={mode === m}
              onClick={() => setMode(m)}
              className={`px-3 py-1.5 text-sm ${mode === m ? 'bg-[var(--color-accent)] text-[var(--color-accent-contrast)]' : 'bg-[var(--color-bg-raised)] text-[var(--color-text)]'}`}
            >
              {m === 'lista' ? t.list : t.cards}
            </button>
          ))}
        </div>
        <select
          aria-label={t.topic}
          className={selectClass}
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        >
          <option value="all">{t.allTopics}</option>
          {topics.map((x) => (
            <option key={x} value={x}>
              {x}
            </option>
          ))}
        </select>
        <select
          aria-label="Nivel"
          className={selectClass}
          value={level}
          onChange={(e) => setLevel(e.target.value)}
        >
          {Object.entries(LEVEL_LABEL[lang]).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
        <select
          aria-label="Tipo"
          className={selectClass}
          value={type}
          onChange={(e) => setType(e.target.value)}
        >
          {Object.entries(TYPE_LABEL[lang]).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
        <input
          type="search"
          aria-label={t.search}
          placeholder={t.search}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className={`${selectClass} min-w-[12rem] flex-1`}
        />
      </div>

      <p className="mt-3 text-xs text-[var(--color-text-muted)]" aria-live="polite">
        {t.count(filtered.length, questions.length)} · {t.progress(known, review)}
        {(known > 0 || review > 0) && (
          <>
            {' · '}
            <button
              type="button"
              className="text-[var(--color-accent)] underline"
              onClick={() => {
                setMarks({});
                saveMarks({});
              }}
            >
              {t.reset}
            </button>
          </>
        )}
      </p>

      {filtered.length === 0 && (
        <p className="mt-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-6 text-center text-sm text-[var(--color-text-muted)]">
          {t.none}
        </p>
      )}

      {mode === 'lista' && (
        <ul className="mt-4 space-y-3">
          {filtered.map((q) => {
            const isOpen = open.has(q.id);
            return (
              <li
                key={q.id}
                className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4"
              >
                <p className="text-xs text-[var(--color-text-muted)]">
                  {q.topic} · {LEVEL_LABEL[lang][q.level]} · {TYPE_LABEL[lang][q.type]}
                  {marks[q.id] === 'known' && ' · ✓'}
                  {marks[q.id] === 'review' && ' · ↻'}
                </p>
                <p className="mt-1 font-medium text-[var(--color-text)]">{prompt(q)}</p>
                <button
                  type="button"
                  className={`${buttonClass} mt-3`}
                  aria-expanded={isOpen}
                  aria-controls={`ans-${q.id}`}
                  onClick={() => toggle(q.id)}
                >
                  {isOpen ? t.hide : t.show}
                </button>
                {isOpen && (
                  <div
                    id={`ans-${q.id}`}
                    className="mt-3 border-l-4 border-[var(--color-accent)] pl-3"
                  >
                    <p className="text-xs font-semibold tracking-wide text-[var(--color-accent)] uppercase">
                      {t.answer}
                    </p>
                    <p className="mt-1 text-sm text-[var(--color-text)]">{answer(q)}</p>
                    <div className="mt-3 flex gap-2">
                      <button
                        type="button"
                        className={buttonClass}
                        onClick={() => mark(q.id, 'known')}
                      >
                        {t.known}
                      </button>
                      <button
                        type="button"
                        className={buttonClass}
                        onClick={() => mark(q.id, 'review')}
                      >
                        {t.review}
                      </button>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}

      {mode === 'flashcards' && card && (
        <div className="mt-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-6">
          <p className="text-xs text-[var(--color-text-muted)]">
            {t.cardOf(Math.min(cursor, cards.length - 1) + 1, cards.length)} · {card.topic} ·{' '}
            {LEVEL_LABEL[lang][card.level]}
          </p>
          <p className="mt-3 text-lg font-semibold text-[var(--color-text)]">{prompt(card)}</p>
          <button
            type="button"
            className={`${buttonClass} mt-4`}
            aria-expanded={cardOpen}
            onClick={() => toggle(card.id)}
          >
            {cardOpen ? t.hide : t.show}
          </button>
          {cardOpen && (
            <div className="mt-4 border-l-4 border-[var(--color-accent)] pl-3">
              <p className="text-xs font-semibold tracking-wide text-[var(--color-accent)] uppercase">
                {t.answer}
              </p>
              <p className="mt-1 text-sm text-[var(--color-text)]">{answer(card)}</p>
            </div>
          )}
          <div className="mt-5 flex flex-wrap gap-2">
            <button
              type="button"
              className={buttonClass}
              onClick={() => {
                mark(card.id, 'known');
                next();
              }}
            >
              {t.known}
            </button>
            <button
              type="button"
              className={buttonClass}
              onClick={() => {
                mark(card.id, 'review');
                next();
              }}
            >
              {t.review}
            </button>
            <button type="button" className={buttonClass} onClick={next}>
              {t.next}
            </button>
            <button
              type="button"
              className={buttonClass}
              onClick={() => {
                setOrder(shuffled(questions.map((q) => q.id)));
                setCursor(0);
              }}
            >
              {t.shuffle}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
