import { useEffect, useRef, useState } from 'react';

interface Props {
  /** Especificación Vega-Lite. */
  spec: Record<string, unknown>;
  alt: string;
  /** Alto reservado (px) antes de que cargue el gráfico: evita saltos de maquetación. */
  minHeight?: number;
}

function themeConfig(): Record<string, unknown> {
  const css = getComputedStyle(document.documentElement);
  const read = (name: string, fallback: string) => css.getPropertyValue(name).trim() || fallback;
  const text = read('--color-text', '#0f172a');
  const muted = read('--color-text-muted', '#475569');
  const border = read('--color-border', '#e2e8f0');
  return {
    background: 'transparent',
    view: { stroke: border },
    axis: {
      labelColor: muted,
      titleColor: text,
      domainColor: border,
      tickColor: border,
      gridColor: border,
    },
    header: { labelColor: text, titleColor: text },
    legend: { labelColor: muted, titleColor: text },
    title: { color: text },
  };
}

/** Número que cambia cuando cambia el tema (botón de tema o preferencia del sistema). */
function useThemeVersion(): number {
  const [version, setVersion] = useState(0);
  useEffect(() => {
    const bump = () => setVersion((v) => v + 1);
    const observer = new MutationObserver(bump);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    });
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    media.addEventListener('change', bump);
    return () => {
      observer.disconnect();
      media.removeEventListener('change', bump);
    };
  }, []);
  return version;
}

/** Gráfico Vega-Lite con carga perezosa de vega-embed y colores del tema activo. */
export default function VegaChart({ spec, alt, minHeight = 220 }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const theme = useThemeVersion();

  useEffect(() => {
    let view: { finalize: () => void } | undefined;
    let cancelled = false;
    async function render() {
      const embed = (await import('vega-embed')).default;
      if (cancelled || !ref.current) return;
      const result = await embed(ref.current, spec, {
        actions: false,
        renderer: 'svg',
        config: themeConfig(),
      });
      if (cancelled) {
        result.view.finalize();
        return;
      }
      view = result.view;
    }
    render();
    return () => {
      cancelled = true;
      view?.finalize();
    };
  }, [spec, theme]);

  return (
    <div role="img" aria-label={alt} className="my-5 overflow-x-auto" style={{ minHeight }}>
      <div ref={ref} />
    </div>
  );
}
