// The site lives under a base path on GitHub Pages (https://thebreadishard.github.io/spectrum-atlas/). Every internal link goes through here.
const raw = import.meta.env.BASE_URL || '/';
export const base = raw.endsWith('/') ? raw.slice(0, -1) : raw;   // '' at the root, '/spectrum-atlas' on Pages
export const withBase = (p: string) => `${base}${p.startsWith('/') ? p : '/' + p}`;
