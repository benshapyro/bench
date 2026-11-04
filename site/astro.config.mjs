import { defineConfig } from 'astro/config';

// Static site: every page is pre-built from ../data at build time.
export default defineConfig({
  site: 'https://bench.shapyro.com',
  output: 'static',
});
