// Build-time endpoint: a compact copy of the catalogue for the client-side search (design §4.2, BACKLOG step 6).
// Columns: id, name, formula, smiles, layer, rung, n_heavy. Loaded by the atlas island on the first keystroke, never on page load.
import type { APIRoute } from 'astro';
import catalog from '../../../../export/out/catalog.json';

export const GET: APIRoute = () => {
  const cols = ['id', 'name', 'formula', 'smiles', 'layer', 'rung', 'n_heavy'];
  const rows = (catalog as any[]).map((r) => [r.id, r.name, r.formula ?? '', r.smiles ?? '', r.layer, r.rung, r.n_heavy ?? null]);
  return new Response(JSON.stringify({ cols, rows }), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
};
