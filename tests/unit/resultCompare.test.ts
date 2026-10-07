import { describe, expect, it } from 'vitest';
import { compareResultSets } from '../../src/lib/resultCompare';

describe('compareResultSets', () => {
  it('coincide cuando las filas son idénticas', () => {
    const expected = [
      { month: 1, revenue: 100 },
      { month: 2, revenue: 200 },
    ];
    const actual = [
      { month: 1, revenue: 100 },
      { month: 2, revenue: 200 },
    ];
    expect(compareResultSets(expected, actual).match).toBe(true);
  });

  it('por defecto el orden de filas no importa', () => {
    const expected = [
      { month: 1, revenue: 100 },
      { month: 2, revenue: 200 },
    ];
    const actual = [
      { month: 2, revenue: 200 },
      { month: 1, revenue: 100 },
    ];
    expect(compareResultSets(expected, actual).match).toBe(true);
  });

  it('con orderMatters, el orden sí importa', () => {
    const expected = [
      { month: 1, revenue: 100 },
      { month: 2, revenue: 200 },
    ];
    const actual = [
      { month: 2, revenue: 200 },
      { month: 1, revenue: 100 },
    ];
    const result = compareResultSets(expected, actual, { orderMatters: true });
    expect(result.match).toBe(false);
    expect(result.message).toMatch(/ORDER BY/);
  });

  it('detecta filas de más con un mensaje claro', () => {
    const expected = [{ x: 1 }];
    const actual = [{ x: 1 }, { x: 2 }, { x: 3 }];
    const result = compareResultSets(expected, actual);
    expect(result.match).toBe(false);
    expect(result.message).toContain('sobran 2 filas');
  });

  it('detecta filas de menos con un mensaje claro', () => {
    const expected = [{ x: 1 }, { x: 2 }];
    const actual = [{ x: 1 }];
    const result = compareResultSets(expected, actual);
    expect(result.match).toBe(false);
    expect(result.message).toContain('faltan 1 fila');
  });

  it('respeta la tolerancia de punto flotante', () => {
    const expected = [{ avg: 10.00001 }];
    const actual = [{ avg: 10.00002 }];
    expect(compareResultSets(expected, actual, { floatTolerance: 1e-3 }).match).toBe(true);
    expect(compareResultSets(expected, actual, { floatTolerance: 1e-9 }).match).toBe(false);
  });

  it('avisa si faltan columnas esperadas', () => {
    const expected = [{ month: 1, revenue: 100 }];
    const actual = [{ month: 1 }];
    const result = compareResultSets(expected, actual);
    expect(result.match).toBe(false);
    expect(result.message).toContain('revenue');
  });

  it('con ignoreColumnNames compara solo por posición', () => {
    const expected = [{ mes: 1, total: 100 }];
    const actual = [{ month_number: 1, sum_revenue: 100 }];
    expect(compareResultSets(expected, actual, { ignoreColumnNames: true }).match).toBe(true);
  });

  it('columns restringe la comparación a un subconjunto', () => {
    const expected = [{ month: 1, revenue: 100 }];
    const actual = [{ month: 1, revenue: 100, extra_debug_col: 'x' }];
    expect(compareResultSets(expected, actual, { columns: ['month', 'revenue'] }).match).toBe(true);
  });

  it('dos result sets vacíos coinciden', () => {
    expect(compareResultSets([], []).match).toBe(true);
  });
});
