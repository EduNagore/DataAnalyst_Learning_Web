interface Props {
  columns: string[];
  rows: Record<string, unknown>[];
  truncated?: boolean;
  elapsedMs?: number;
}

function formatCell(value: unknown): { text: string; numeric: boolean; isNull: boolean } {
  if (value === null || value === undefined) return { text: 'NULL', numeric: false, isNull: true };
  if (typeof value === 'number') {
    return {
      text: Number.isInteger(value)
        ? value.toLocaleString('es-ES')
        : value.toLocaleString('es-ES', { maximumFractionDigits: 6 }),
      numeric: true,
      isNull: false,
    };
  }
  if (typeof value === 'boolean')
    return { text: value ? 'true' : 'false', numeric: false, isNull: false };
  return { text: String(value), numeric: false, isNull: false };
}

export default function ResultTable({ columns, rows, truncated, elapsedMs }: Props) {
  return (
    <div>
      <p className="mb-2 text-xs text-[var(--color-text-muted)]" role="status">
        {rows.length.toLocaleString('es-ES')} {rows.length === 1 ? 'fila' : 'filas'}
        {truncated ? ' (resultado recortado; hay más)' : ''}
        {elapsedMs !== undefined ? ` · ${Math.round(elapsedMs)} ms` : ''}
      </p>
      <div className="max-h-96 overflow-auto rounded-md border border-[var(--color-border)]">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-[var(--color-bg-subtle)]">
            <tr>
              {columns.map((c) => (
                <th
                  key={c}
                  scope="col"
                  className="px-3 py-2 font-mono font-semibold text-[var(--color-text)]"
                >
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="border-t border-[var(--color-border)]/60">
                {columns.map((c) => {
                  const cell = formatCell(row[c]);
                  return (
                    <td
                      key={c}
                      className={
                        'px-3 py-1.5 font-mono whitespace-nowrap ' +
                        (cell.numeric ? 'text-right ' : '') +
                        (cell.isNull
                          ? 'text-[var(--color-text-muted)] italic'
                          : 'text-[var(--color-text)]')
                      }
                    >
                      {cell.text}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
