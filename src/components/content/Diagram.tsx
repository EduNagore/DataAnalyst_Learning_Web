import { useEffect, useId, useRef, useState } from 'react';

interface Props {
  /** Definición Mermaid (erDiagram, flowchart, etc.). */
  chart: string;
  /** Texto alternativo para lectores de pantalla (describe la conclusión, no solo "diagrama"). */
  alt: string;
}

/**
 * Envoltorio de Mermaid con carga perezosa (ver PLAN.md §11: nunca cargar
 * fuera de donde se usa). Pensado para `client:visible`.
 */
export default function Diagram({ chart, alt }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const id = `diagram-${useId().replace(/[:]/g, '')}`;

  useEffect(() => {
    let cancelled = false;
    async function render() {
      try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
        const { svg } = await mermaid.render(id, chart);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        if (!cancelled)
          setError(err instanceof Error ? err.message : 'Error al renderizar el diagrama');
      }
    }
    render();
    return () => {
      cancelled = true;
    };
  }, [chart, id]);

  if (error) {
    return (
      <pre className="overflow-x-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-4 text-xs text-[var(--color-danger)]">
        No se pudo renderizar el diagrama: {error}
      </pre>
    );
  }

  return (
    <div
      ref={containerRef}
      role="img"
      aria-label={alt}
      className="overflow-x-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4 [&_svg]:mx-auto"
    >
      <p className="text-sm text-[var(--color-text-muted)]">Cargando diagrama…</p>
    </div>
  );
}
