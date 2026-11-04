# Bench site

Static site built with [Astro](https://astro.build). Every number comes from `../data/` at build time.

```
npm install
npm run dev      # local preview at http://localhost:4321
npm run build    # writes dist/
```

- `src/lib/data.ts` turns the data files into what the page needs. The only hand-written text there is how each job is worded on the page.
- `src/lib/home.client.js` is the page's calculator: score as % of the best, best value at the bar, and the monthly bill (spec section 5).
- `src/pages/method.astro` renders `../docs/METHOD.md`.
- Defaults (bar, volume, caching) live in `../data/site.json`.

Until the usage run, the thinking cost uses a placeholder multiplier per reasoning level, and the page says costs are estimates.
