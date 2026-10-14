import { python } from '@codemirror/lang-python';
import { PostgreSQL, sql } from '@codemirror/lang-sql';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { Prec } from '@codemirror/state';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorView, keymap } from '@codemirror/view';
import { tags } from '@lezer/highlight';
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

/**
 * Ajustes de contraste (WCAG AA) sobre el tema oscuro One Dark: sus comentarios, números de línea y algunos
 * colores de sintaxis quedan por debajo de 4,5:1 sobre su fondo.
 */
const darkContrast = [
  Prec.highest(
    EditorView.theme(
      {
        '.cm-gutters': { color: '#aab4c5' },
        '.cm-activeLineGutter': { color: '#d7dde8' },
      },
      { dark: true },
    ),
  ),
  Prec.highest(
    syntaxHighlighting(
      HighlightStyle.define([
        { tag: [tags.comment, tags.lineComment, tags.blockComment], color: '#a9b3c4' },
        {
          tag: [
            tags.keyword,
            tags.operatorKeyword,
            tags.controlKeyword,
            tags.definitionKeyword,
            tags.moduleKeyword,
          ],
          color: '#d9a0ee',
        },
        {
          tag: [tags.propertyName, tags.name, tags.deleted, tags.character, tags.macroName],
          color: '#f08f98',
        },
      ]),
    ),
  ),
];

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
    // El nombre accesible del área editable (si no, lectores de pantalla y Lighthouse no la identifican).
    const a11y = EditorView.contentAttributes.of({ 'aria-label': label, tabindex: '0' });
    return [lang, a11y, ...(dark ? darkContrast : []), ...run];
  }, [language, schema, onRun, label, dark]);

  return (
    <div
      className="overflow-hidden rounded-md border border-[var(--color-border)]"
      role="group"
      aria-label={label}
      // Reserva el alto desde el HTML estático para que el editor (solo cliente) no empuje el resto de la página.
      style={{ minHeight }}
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
