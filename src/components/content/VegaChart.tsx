import { useEffect, useRef } from 'react';

interface Props {
  /** Especificación Vega-Lite. */
  spec: Record<string, unknown>;
  alt: string;
}

/** Gráfico Vega-Lite con carga perezosa de vega-embed. */
export default function VegaChart({ spec, alt }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let view: { finalize: () => void } | undefined;
    let cancelled = false;
    async function render() {
      const embed = (await import('vega-embed')).default;
      if (cancelled || !ref.current) return;
      const result = await embed(ref.current, spec, { actions: false, renderer: 'svg' });
      view = result.view;
    }
    render();
    return () => {
      cancelled = true;
      view?.finalize();
    };
  }, [spec]);

  return <div ref={ref} role="img" aria-label={alt} className="my-5 overflow-x-auto" />;
}
