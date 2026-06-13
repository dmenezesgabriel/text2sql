import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

export class DataTableElement extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      width: 100%;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-family: var(--font-sans, sans-serif);
      font-size: 14px;
    }
    th {
      background: var(--color-bg-secondary, #f5f5f5);
      padding: 8px 12px;
      text-align: left;
      font-weight: 600;
      border-bottom: 2px solid var(--color-border, #e0e0e0);
    }
    td {
      padding: 8px 12px;
      border-bottom: 1px solid var(--color-border, #e0e0e0);
    }
    tr:hover td {
      background: var(--color-bg-secondary, #f5f5f5);
    }
    .title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 12px;
    }
  `;

  @property({ type: String }) title = '';
  @property({ type: Array })
  columns: { key: string; header: string; format?: string }[] = [];
  @property({ type: Array }) rows: Record<string, unknown>[] = [];

  render() {
    return html`
      ${this.title ? html`<div class="title">${this.title}</div>` : ''}
      <table>
        <thead>
          <tr>
            ${this.columns.map((col) => html`<th>${col.header}</th>`)}
          </tr>
        </thead>
        <tbody>
          ${this.rows.map(
            (row) => html`
              <tr>
                ${this.columns.map((col) => html`<td>${row[col.key] ?? ''}</td>`)}
              </tr>
            `,
          )}
        </tbody>
      </table>
    `;
  }
}

customElements.define('bi-data-table', DataTableElement);
