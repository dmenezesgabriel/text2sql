import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

type Column = { key: string; header: string; format?: string };

const NUMERIC_FORMATS = new Set(['number', 'currency', 'percent', 'integer', 'float', 'decimal']);

export class DataTableElement extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      width: 100%;
    }
    .title {
      font-size: var(--text-2xs);
      font-weight: var(--weight-semibold);
      letter-spacing: var(--tracking-caps);
      text-transform: uppercase;
      color: var(--color-text-secondary);
      margin-bottom: var(--spacing-sm);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-family: var(--font-sans, sans-serif);
      font-size: var(--text-base);
      color: var(--color-text);
    }
    /* Headers: small-caps, no fill — a single hairline rule does the separating. */
    th {
      padding: var(--spacing-xs) var(--spacing-sm);
      text-align: left;
      font-size: var(--text-2xs);
      font-weight: var(--weight-semibold);
      letter-spacing: var(--tracking-caps);
      text-transform: uppercase;
      color: var(--color-text-secondary);
      border-bottom: 1px solid var(--color-border-strong);
      white-space: nowrap;
    }
    td {
      padding: var(--spacing-xs) var(--spacing-sm);
      border-bottom: 1px solid var(--color-grid-line);
    }
    /* Numbers right-align and use tabular figures so columns line up by digit. */
    th.numeric,
    td.numeric {
      text-align: right;
      font-variant-numeric: tabular-nums;
    }
    tbody tr:last-child td {
      border-bottom: none;
    }
    tbody tr:hover td {
      background: var(--color-bg-secondary);
    }
  `;

  @property({ type: String }) title = '';
  @property({ type: Array }) columns: Column[] = [];
  @property({ type: Array }) rows: Record<string, unknown>[] = [];

  private _isNumeric(col: Column): boolean {
    if (col.format && NUMERIC_FORMATS.has(col.format.toLowerCase())) return true;
    const sample = this.rows.find((r) => r[col.key] != null);
    return sample !== undefined && typeof sample[col.key] === 'number';
  }

  render() {
    // Precompute the per-column alignment class so the cell templates stay short.
    const cols = this.columns.map((col) => ({
      key: col.key,
      header: col.header,
      cls: this._isNumeric(col) ? 'numeric' : '',
    }));
    return html`
      ${this.title ? html`<div class="title">${this.title}</div>` : ''}
      <table>
        <thead>
          <tr>
            ${cols.map((c) => html`<th class=${c.cls}>${c.header}</th>`)}
          </tr>
        </thead>
        <tbody>
          ${this.rows.map(
            (row) => html`
              <tr>
                ${cols.map((c) => html`<td class=${c.cls}>${row[c.key] ?? ''}</td>`)}
              </tr>
            `,
          )}
        </tbody>
      </table>
    `;
  }
}

customElements.define('bi-data-table', DataTableElement);
