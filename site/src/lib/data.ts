// Builds everything the home page needs from the repo's data/ folder at build time.
// The data files are the single source of truth; nothing here is typed in by hand
// except the plain-English wording for each job.
import results from '../../../data/results.json';
import models from '../../../data/models.json';
import jobs from '../../../data/jobs.json';
import benchmarks from '../../../data/benchmarks.json';
import site from '../../../data/site.json';
import presets from '../../../usage-run/presets.json';

type AnyObj = Record<string, any>;
const list = (x: any, key: string): AnyObj[] => (Array.isArray(x) ? x : x[key]);

// Short ids used by the page script, and the wording the page shows for each job.
const UI: Record<string, AnyObj> = {
  'general-business-work': { short: 'business', preset: 'writing_and_analysis', long: 'business work', ex: 'finance, coding, legal and tax work', unit: 'report', units: 'reports', within: false,
    what: 'Independent test of professional work in finance, coding, legal and tax, run by Vals AI.' },
  'customer-service': { short: 'support', preset: 'customer_service', long: 'customer service', ex: 'answering customers while following company policy', unit: 'conversation', units: 'conversations', within: true,
    what: 'An AI agent answers banking customers by finding the right policy in about 700 documents and taking the right actions.' },
  'using-software': { short: 'software', preset: 'using_software', long: 'using software for us', ex: 'filling in forms, moving data between apps', unit: 'task', units: 'tasks in apps', within: true,
    what: 'An AI agent operates a real computer to finish long, multi-step tasks across ordinary apps. Scores here come from the labs themselves.' },
  'building-software': { short: 'code', preset: 'building_software', long: 'writing code', ex: 'writing and fixing code', unit: 'fix or feature', units: 'fixes and features', within: true,
    what: 'An AI agent completes 66 hard, real-world tasks in a computer terminal, each checked by automated tests. Run by Vals AI with the same setup for every model.' },
  'reading-documents': { short: 'docs', preset: 'reading_documents', long: 'reading documents', ex: 'pulling numbers from charts, scans and PDFs', unit: 'document', units: 'documents', within: false,
    what: 'Professionals wrote questions about 100 real PDFs, like leases and datasheets. A task only passes if every required fact is right. Run by Surge AI.' },
};

const benchList = list(benchmarks, 'benchmarks');
const benchById = Object.fromEntries(benchList.map((b) => [b.id, b]));
const presetJobs = (presets as AnyObj).jobs;

export const JOBS = list(jobs, 'jobs').map((j) => {
  const ui = UI[j.id];
  if (!ui) throw new Error(`No page wording for job ${j.id}`);
  const p = presetJobs[ui.preset];
  const b = benchById[j.main_benchmark] ?? {};
  return {
    id: ui.short, name: j.name, long: ui.long, ex: ui.ex, what: ui.what,
    bench: b.name ?? j.main_benchmark, benchUrl: b.source_url ?? b.url ?? '#',
    unit: ui.unit, units: ui.units, within: ui.within,
    pin: p.pages_in, pout: p.pages_out, rep: p.repeated_share,
  };
});

const shortJob = Object.fromEntries(list(jobs, 'jobs').map((j) => [j.main_benchmark, UI[j.id].short]));

const modelList = list(models, 'models');
export const DATA = {
  models: modelList.map((m) => ({
    id: m.id,
    name: String(m.name).replace(/^Claude /, ''),
    lab: m.lab,
    open: !!m.open_weight,
    in: m.prices.input,
    out: m.prices.output,
    cr: m.prices.cache_read ?? m.prices.input,
  })),
  results: list(results, 'results')
    .filter((r) => (r.kind === 'main' && r.reference_conditions_met) || r.kind === 'full_pass')
    .filter((r) => shortJob[r.benchmark])
    .map((r) => ({
      j: shortJob[r.benchmark],
      m: r.model,
      lv: r.reasoning_level?.as_shown ?? 'not stated',
      s: r.score,
      lab: r.label,
      u: r.check?.status !== 'checked',
      fp: r.kind === 'full_pass',
      src: r.source_name,
    })),
};

const fmt = (d: string) =>
  new Date(d + 'T12:00:00Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });

export const CHECKED = fmt(list(results, 'results').map((r) => r.date_recorded).sort().at(-1));
export const PRICES_CHECKED = fmt(modelList.map((m) => m.date_checked).filter(Boolean).sort().at(-1) ?? '2026-10-17');

export const DEFAULTS = {
  bar: (site as AnyObj).default_bar_percent,
  volume: (site as AnyObj).default_volume_tasks_per_month,
  caching: (site as AnyObj).default_caching,
};
