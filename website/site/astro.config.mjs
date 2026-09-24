import { defineConfig } from 'astro/config';

// Spectrum Atlas — static output; the data comes from ../export/out (built by build_catalog.py and depict.py).
// The site URL is a placeholder until the user picks the domain (design §12: GitHub Pages first).
export default defineConfig({
  site: 'https://thebreadishard.github.io',
  base: '/spectrum-atlas',
  output: 'static',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
