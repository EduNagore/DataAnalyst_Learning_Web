import { describe, expect, it } from 'vitest';
import { INTENTS, recommend, type Intent } from '../../src/lib/chartChooser';

describe('chartChooser', () => {
  it('cada intención tiene al menos una variante completa', () => {
    for (const [intent, info] of Object.entries(INTENTS)) {
      expect(info.variants.length, intent).toBeGreaterThan(0);
      for (const v of info.variants) {
        expect(v.id.length).toBeGreaterThan(1);
        for (const field of [v.when, v.chart, v.why, v.avoid])
          expect(field.length).toBeGreaterThan(5);
      }
    }
  });

  it('los identificadores de variante son únicos dentro de cada intención', () => {
    for (const info of Object.values(INTENTS)) {
      const ids = info.variants.map((v) => v.id);
      expect(new Set(ids).size).toBe(ids.length);
    }
  });

  it('recomienda barras ordenadas para comparar pocas categorías y rechaza las tartas', () => {
    const r = recommend('comparar', 'pocas');
    expect(r?.chart).toMatch(/Barras horizontales ordenadas/);
    expect(r?.avoid).toMatch(/Tartas/);
  });

  it('devuelve undefined para una variante inexistente', () => {
    expect(recommend('tiempo' as Intent, 'no-existe')).toBeUndefined();
  });
});
