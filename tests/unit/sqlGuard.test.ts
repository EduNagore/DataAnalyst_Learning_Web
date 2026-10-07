import { describe, expect, it } from 'vitest';
import { guardSql } from '../../src/lib/lab/sqlGuard';

describe('guardSql', () => {
  it.each([
    'SELECT 1',
    'select * from orders;',
    'WITH a AS (SELECT 1) SELECT * FROM a',
    '(SELECT 1) UNION ALL (SELECT 2)',
    'DESCRIBE orders',
    "SELECT 'DROP TABLE x; --' AS texto", // palabras prohibidas dentro de un literal
    '-- comentario con DROP\nSELECT 1',
  ])('acepta %j', (sql) => {
    expect(guardSql(sql).ok).toBe(true);
  });

  it.each([
    ['DROP VIEW orders', /DROP/],
    ['SELECT 1; SELECT 2', /una sentencia/],
    ['INSERT INTO t VALUES (1)', /INSERT/],
    ['', /Escribe/],
    ["ATTACH 'x.db'", /ATTACH/],
    ['WITH a AS (SELECT 1) DELETE FROM t', /DELETE/],
    ["COPY orders TO 'x.csv'", /COPY/],
  ])('rechaza %j', (sql, message) => {
    const result = guardSql(sql);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.message).toMatch(message);
  });

  it('quita el punto y coma final', () => {
    const result = guardSql('SELECT 1;');
    expect(result.ok && result.sql).toBe('SELECT 1');
  });
});
