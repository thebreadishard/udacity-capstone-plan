// Flag labels (27 Sep 2026). The catalog carries machine flags (export/SCHEMA.md); the pages show them as plain sentences. The two
// second-route flags are one story — the finite-difference Hessian was noisy, so the release uses the analytic one — and are shown as one phrase.
export type FlagView = { text: string; title: string };

const LABEL: Record<string, FlagView> = {
  imaginary_mode_under_review: { text: 'imaginary mode, second route pending', title: 'The cheap-level Hessian has an imaginary frequency; the analytic (second-route) Hessian has not been computed yet.' },
  second_route_healed: { text: 'imaginary mode healed by the analytic Hessian', title: 'The finite-difference Hessian showed an imaginary frequency that the analytic Hessian does not: numerical noise, not a saddle point.' },
  imaginary_mode_genuine: { text: 'imaginary mode confirmed', title: 'The analytic Hessian confirms the imaginary frequency: the geometry is not a minimum at this level.' },
  second_route_agrees: { text: 'analytic check agrees', title: 'Analytic Hessian (pyscf) and finite-difference Hessian (psi4) agree within 15 cm⁻¹ on every frequency.' },
  second_route_disagrees: { text: 'finite-difference Hessian noisy (analytic check differs > 15 cm⁻¹)', title: 'The finite-difference Hessian and the analytic Hessian of the same geometry differ by more than 15 cm⁻¹ on at least one frequency; the numerical route is the noisy one.' },
  replaced_by_second_route: { text: 'release uses the analytic Hessian', title: 'In the released training set this molecule carries the analytic Hessian instead of the finite-difference one.' },
  screen_flagged: { text: 'large B3LYP → ωB97X shift, screened', title: 'The two functionals differ by more than 80 cm⁻¹ on some frequency, which sent the molecule to the analytic second route (screen of 23 Sep 2026).' },
};

/** Turn the catalog's flag list into displayable phrases; 'disagrees' + 'replaced' collapse into one causal phrase. */
export function describeFlags(flags: string[]): FlagView[] {
  const set = new Set(flags);
  const out: FlagView[] = [];
  if (set.has('second_route_disagrees') && set.has('replaced_by_second_route')) {
    out.push({ text: 'finite-difference Hessian was noisy → release uses the analytic Hessian',
               title: LABEL.second_route_disagrees.title + ' ' + LABEL.replaced_by_second_route.title });
    set.delete('second_route_disagrees'); set.delete('replaced_by_second_route');
  }
  for (const f of flags) if (set.has(f)) out.push(LABEL[f] ?? { text: f.replaceAll('_', ' '), title: f });
  return out;
}
