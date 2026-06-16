import '@/shared/components/badge/bi-badge';
import '@/shared/components/button/bi-button';
import '@/shared/components/card/bi-card';
import '@/widgets/json-render/components/data-table';
import '@/widgets/json-render/components/metric';

import type { Meta, StoryObj } from '@storybook/web-components';
import { html, type TemplateResult } from 'lit';

/**
 * Living reference for the text2sql design system. Every swatch and sample reads
 * from the same CSS custom properties the app uses, so flipping the Storybook
 * theme toolbar (light/dark) re-tones this page exactly like the product.
 */
const meta: Meta = {
  title: 'Design System/Overview',
  parameters: { layout: 'fullscreen' },
};
export default meta;

// ---- shared page chrome -------------------------------------------------------

const pageStyles = html`
  <style>
    .ds {
      padding: 32px;
      background: var(--color-bg);
      color: var(--color-text);
      font-family: var(--font-sans);
      min-height: 100vh;
    }
    .ds h2 {
      font-size: var(--text-lg);
      font-weight: var(--weight-semibold);
      letter-spacing: var(--tracking-tight);
      margin: 0 0 4px;
    }
    .ds .lede {
      color: var(--color-text-secondary);
      font-size: var(--text-sm);
      margin: 0 0 24px;
      max-width: 60ch;
    }
    .ds h3 {
      font-size: var(--text-2xs);
      font-weight: var(--weight-semibold);
      letter-spacing: var(--tracking-caps);
      text-transform: uppercase;
      color: var(--color-text-secondary);
      margin: 28px 0 12px;
    }
    .ds-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
      gap: 12px;
    }
    .ds-swatch {
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      overflow: hidden;
      background: var(--color-surface);
    }
    .ds-chip {
      height: 56px;
    }
    .ds-meta {
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .ds-name {
      font-size: var(--text-sm);
      font-weight: var(--weight-medium);
    }
    .ds-val {
      font-family: var(--font-mono);
      font-size: var(--text-2xs);
      color: var(--color-text-secondary);
    }
    .ds-row {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: flex-end;
    }
    .ds-box {
      background: var(--color-primary);
      border-radius: var(--radius-sm);
    }
  </style>
`;

const page = (title: string, lede: string, body: TemplateResult) => html`
  ${pageStyles}
  <div class="ds">
    <h2>${title}</h2>
    <p class="lede">${lede}</p>
    ${body}
  </div>
`;

const swatch = (name: string, value: string, varRef = `var(${name})`) => html`
  <div class="ds-swatch">
    <div class="ds-chip" style="background:${varRef}"></div>
    <div class="ds-meta">
      <span class="ds-name">${name.replace('--', '')}</span>
      <span class="ds-val">${value}</span>
    </div>
  </div>
`;

// ---- Colors -------------------------------------------------------------------

const grays: [string, string][] = [
  ['--gray-0', '#ffffff'],
  ['--gray-25', '#fbfbfc'],
  ['--gray-50', '#f6f7f8'],
  ['--gray-100', '#eceef1'],
  ['--gray-200', '#e2e5ea'],
  ['--gray-300', '#ccd1d9'],
  ['--gray-400', '#a3abb6'],
  ['--gray-500', '#79818d'],
  ['--gray-600', '#5a626d'],
  ['--gray-700', '#3d434c'],
  ['--gray-800', '#23272e'],
  ['--gray-900', '#15181d'],
  ['--gray-950', '#0c0e12'],
];

const accents: [string, string][] = [
  ['--indigo-300', '#9aa0ec'],
  ['--indigo-400', '#7c84e3'],
  ['--indigo-500', '#5b63d3'],
  ['--indigo-600', '#4a51bd'],
];

const status: [string, string][] = [
  ['--color-success', 'success'],
  ['--color-warning', 'warning'],
  ['--color-error', 'error'],
];

const viz: [string, string][] = [
  ['--viz-1', '#5b63d3'],
  ['--viz-2', '#3a9bb5'],
  ['--viz-3', '#6a994e'],
  ['--viz-4', '#bc6c25'],
  ['--viz-5', '#9b5de5'],
  ['--viz-6', '#c1495a'],
];

const semantic: [string, string][] = [
  ['--color-bg', 'page background'],
  ['--color-surface', 'raised surface'],
  ['--color-bg-secondary', 'inset / hover'],
  ['--color-text', 'primary text'],
  ['--color-text-secondary', 'secondary text'],
  ['--color-border', 'hairline'],
  ['--color-grid-line', 'data rules'],
];

export const Colors: StoryObj = {
  render: () =>
    page(
      'Color',
      'A cool-neutral grayscale spine with a single muted indigo accent. Status and chart series stay restrained. Semantic tokens remap per theme — primitives never change.',
      html`
        <h3>Neutral ramp</h3>
        <div class="ds-grid">${grays.map(([n, v]) => swatch(n, v))}</div>
        <h3>Accent — indigo</h3>
        <div class="ds-grid">${accents.map(([n, v]) => swatch(n, v))}</div>
        <h3>Status</h3>
        <div class="ds-grid">${status.map(([n, v]) => swatch(n, v))}</div>
        <h3>Chart series (categorical)</h3>
        <div class="ds-grid">${viz.map(([n, v]) => swatch(n, v))}</div>
        <h3>Semantic — remaps per theme</h3>
        <div class="ds-grid">${semantic.map(([n, v]) => swatch(n, v))}</div>
      `,
    ),
};

// ---- Typography ---------------------------------------------------------------

const scale: [string, string][] = [
  ['--text-2xl', '30px'],
  ['--text-xl', '24px'],
  ['--text-lg', '20px'],
  ['--text-md', '16px'],
  ['--text-base', '14px'],
  ['--text-sm', '12px'],
  ['--text-xs', '11px'],
  ['--text-2xs', '10px'],
];

export const Typography: StoryObj = {
  render: () =>
    page(
      'Typography',
      'Inter for text and UI, JetBrains Mono for code and identifiers. The personality is in the numeric treatment — tabular figures everywhere data appears — not a display face.',
      html`
        <h3>Type scale</h3>
        ${scale.map(
          ([n, v]) => html`
            <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:8px">
              <span class="ds-val" style="width:120px">${n.replace('--', '')} · ${v}</span>
              <span style="font-size:var(${n})">Querying revenue by region</span>
            </div>
          `,
        )}
        <h3>Weights</h3>
        <div class="ds-row" style="font-size:var(--text-md)">
          <span style="font-weight:var(--weight-normal)">Regular 400</span>
          <span style="font-weight:var(--weight-medium)">Medium 500</span>
          <span style="font-weight:var(--weight-semibold)">Semibold 600</span>
          <span style="font-weight:var(--weight-bold)">Bold 700</span>
        </div>
        <h3>Data treatment — tabular numerics</h3>
        <div
          style="font-variant-numeric:tabular-nums;font-size:var(--text-md);font-family:var(--font-mono);line-height:1.6"
        >
          <div>1,204,889.50</div>
          <div>&nbsp;&nbsp;&nbsp;98,210.00</div>
          <div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1,337.25</div>
        </div>
        <h3>Small-caps label</h3>
        <span class="label-caps">Monthly recurring revenue</span>
      `,
    ),
};

// ---- Spacing & Radius ---------------------------------------------------------

const spacing: [string, string][] = [
  ['--spacing-2xs', '2px'],
  ['--spacing-xs', '4px'],
  ['--spacing-sm', '8px'],
  ['--spacing-md', '16px'],
  ['--spacing-lg', '24px'],
  ['--spacing-xl', '32px'],
  ['--spacing-2xl', '48px'],
];

const radii: [string, string][] = [
  ['--radius-sm', '3px'],
  ['--radius-md', '5px'],
  ['--radius-lg', '8px'],
];

export const SpacingAndRadius: StoryObj = {
  render: () =>
    page(
      'Spacing & Radius',
      'An 8px-based spacing rhythm and tight corner radii. Restraint here is what reads as Linear-grade precision.',
      html`
        <h3>Spacing</h3>
        ${spacing.map(
          ([n, v]) => html`
            <div style="display:flex;align-items:center;gap:16px;margin-bottom:8px">
              <span class="ds-val" style="width:130px">${n.replace('--', '')} · ${v}</span>
              <span class="ds-box" style="width:var(${n});height:16px"></span>
            </div>
          `,
        )}
        <h3>Radius</h3>
        <div class="ds-row">
          ${radii.map(
            ([n, v]) => html`
              <div style="text-align:center">
                <div class="ds-box" style="width:72px;height:72px;border-radius:var(${n})"></div>
                <span class="ds-val">${v}</span>
              </div>
            `,
          )}
        </div>
      `,
    ),
};

// ---- Elevation ----------------------------------------------------------------

export const Elevation: StoryObj = {
  render: () =>
    page(
      'Elevation & Borders',
      'Tufte discipline: hairline borders do the separating, shadows barely whisper. Cards sit on the surface — no floating chrome.',
      html`
        <div class="ds-row" style="gap:24px">
          ${[
            ['Hairline border', 'border:1px solid var(--color-border)'],
            ['shadow-sm', 'box-shadow:var(--shadow-sm)'],
            ['shadow-md', 'box-shadow:var(--shadow-md)'],
            ['shadow-lg', 'box-shadow:var(--shadow-lg)'],
          ].map(
            ([label, style]) => html`
              <div style="text-align:center">
                <div
                  style="width:140px;height:88px;border-radius:var(--radius-md);background:var(--color-surface);${style}"
                ></div>
                <span class="ds-val">${label}</span>
              </div>
            `,
          )}
        </div>
      `,
    ),
};

// ---- Components ---------------------------------------------------------------

const sampleColumns = [
  { key: 'region', header: 'Region' },
  { key: 'orders', header: 'Orders', format: 'number' },
  { key: 'revenue', header: 'Revenue', format: 'currency' },
];
const sampleRows = [
  { region: 'North America', orders: 4821, revenue: '1,204,889' },
  { region: 'EMEA', orders: 3190, revenue: '842,110' },
  { region: 'APAC', orders: 2044, revenue: '512,337' },
];

export const Components: StoryObj = {
  render: () =>
    page(
      'Components',
      'The shared primitives and data widgets, retoned to the system. The data table is the signature — small-caps headers, hairline rules, right-aligned tabular numbers.',
      html`
        <h3>Buttons</h3>
        <div class="ds-row">
          <bi-button variant="primary">Primary</bi-button>
          <bi-button variant="secondary">Secondary</bi-button>
          <bi-button variant="ghost">Ghost</bi-button>
          <bi-button variant="danger">Danger</bi-button>
        </div>
        <h3>Badges</h3>
        <div class="ds-row">
          <bi-badge variant="default">default</bi-badge>
          <bi-badge variant="primary">CHART</bi-badge>
          <bi-badge variant="success">Active</bi-badge>
          <bi-badge variant="warning">Stale</bi-badge>
          <bi-badge variant="error">Failed</bi-badge>
          <bi-badge variant="mono">VARCHAR</bi-badge>
        </div>
        <h3>Metric</h3>
        <div class="ds-row">
          <bi-metric
            .label=${'Monthly revenue'}
            .value=${'$1,204,889'}
            .change=${'+12.4%'}
            .direction=${'up'}
            style="width:200px"
          ></bi-metric>
          <bi-metric
            .label=${'Churn'}
            .value=${'2.1%'}
            .change=${'-0.3%'}
            .direction=${'down'}
            style="width:200px"
          ></bi-metric>
        </div>
        <h3>Card</h3>
        <bi-card heading="Quarterly summary" style="max-width:520px;display:block">
          <bi-data-table
            .title=${'Revenue by region'}
            .columns=${sampleColumns}
            .rows=${sampleRows}
          ></bi-data-table>
        </bi-card>
      `,
    ),
};
