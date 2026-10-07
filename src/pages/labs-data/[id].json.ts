import { getCollection } from 'astro:content';
import YAML from 'yaml';
import { labIdOf } from '../../lib/labs';

/**
 * Solución y checks de cada lab, servidos como JSON estático y cargados solo
 * al pulsar «Comprobar» o «Ver solución» (no van en el HTML de la página).
 * Los labs SQL se corrigen en el navegador comparando con la solución.
 */
const solutions = import.meta.glob('/src/content/labs/*/solution.sql', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>;
const pySolutions = import.meta.glob('/src/content/labs/*/solution.py', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>;
const pyTests = import.meta.glob('/src/content/labs/*/test_lab.py', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>;
const checkFiles = import.meta.glob('/src/content/labs/*/checks.yaml', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>;

export async function getStaticPaths() {
  const labs = await getCollection('labs');
  return labs.map((lab) => ({ params: { id: labIdOf(lab.id) } }));
}

export function GET({ params }: { params: { id: string } }) {
  const pySolution = pySolutions[`/src/content/labs/${params.id}/solution.py`];
  const tests = pyTests[`/src/content/labs/${params.id}/test_lab.py`];
  if (pySolution !== undefined && tests !== undefined) {
    return new Response(JSON.stringify({ solution: pySolution.trim(), tests }), {
      headers: { 'Content-Type': 'application/json' },
    });
  }
  const solution = solutions[`/src/content/labs/${params.id}/solution.sql`];
  const rawChecks = checkFiles[`/src/content/labs/${params.id}/checks.yaml`];
  if (solution === undefined || rawChecks === undefined) {
    return new Response('Lab no encontrado', { status: 404 });
  }
  return new Response(
    JSON.stringify({ solution: solution.trim(), checks: YAML.parse(rawChecks) ?? {} }),
    {
      headers: { 'Content-Type': 'application/json' },
    },
  );
}
