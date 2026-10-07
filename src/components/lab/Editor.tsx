import { python } from '@codemirror/lang-python';
import { PostgreSQL, sql } from '@codemirror/lang-sql';
import { Prec } from '@codemirror/state';
import { oneDark } from '@codemirror/theme-one-dark';
import { keymap } from '@codemirror/view';
import CodeMirror from '@uiw/react-codemirror';
import { useEffect, useMemo, useState } from 'react';

interface Props {
  value: string;
  onChange: (value: string) => void;
  language: 'sql' | 'python';
  /** Esquema para el autocompletado SQL: { tabla: [columnas] }. */
  schema?: Record<string, string[]>;
  /** Ctrl/Cmd + Enter. */
  onRun?: () => void;
  minHeight?: string;
  label: string;
}

function useIsDark(): boolean {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const compute = () => {
      const explicit = document.documentElement.getAttribute('data-theme');
      setDark(
        explicit ? explicit === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches,
      );
    };
    compute();
    const observer = new MutationObserver(compute);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    });
    return () => observer.disconnect();
  }, []);
  return dark;
}

export default function Editor({
  value,
  onChange,
  language,
  schema,
  onRun,
  minHeight = '12rem',
  label,
}: Props) {
  const dark = useIsDark();

  const extensions = useMemo(() => {
    const lang =
      language === 'sql' ? sql({ dialect: PostgreSQL, schema, upperCaseKeywords: true }) : python();
    const run = onRun
      ? [
          Prec.highest(
            keymap.of([
              {
                key: 'Mod-Enter',
                run: () => {
                  onRun();
                  return true;
                },
              },
            ]),
          ),
        ]
      : [];
    return [lang, ...run];
  }, [language, schema, onRun]);

  return (
    <div
      className="overflow-hidden rounded-md border border-[var(--color-border)]"
      role="group"
      aria-label={label}
    >
      <CodeMirror
        value={value}
        onChange={onChange}
        extensions={extensions}
        theme={dark ? oneDark : 'light'}
        minHeight={minHeight}
        basicSetup={{ lineNumbers: true, foldGutter: false, highlightActiveLine: true }}
      />
    </div>
  );
}
