import '@/shared/components/card/bi-card';
import '@/shared/components/page-header/bi-page-header';
import '@/shared/components/spinner/bi-spinner';

import { css, html, LitElement, nothing } from 'lit';
import { property, state } from 'lit/decorators.js';

import type { Dataset } from '@/entities/dataset/types';
import { listDatasets, previewDataset } from '@/features/dataset/api/dataset-api';

interface Preview {
  columns: string[];
  rows: Record<string, unknown>[];
}

/**
 *
 * @param val
 */
function cellStr(val: unknown): string {
  switch (typeof val) {
    case 'string': {
      return val;
    }
    case 'number':
    case 'boolean':
    case 'bigint': {
      return String(val);
    }
    case 'undefined': {
      return '';
    }
    default: {
      return val === null ? '' : JSON.stringify(val);
    }
  }
}

export class BiDatasetDetail extends LitElement {
  static readonly styles = css`
    :host {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-lg);
    }
    .error {
      font-size: var(--text-sm);
      color: var(--color-error);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: var(--text-sm);
      overflow-x: auto;
      display: block;
    }
    th,
    td {
      text-align: left;
      padding: var(--spacing-sm) var(--spacing-md);
      border-bottom: 1px solid var(--color-border);
      white-space: nowrap;
    }
    th {
      font-weight: 600;
      color: var(--color-text-secondary);
    }
  `;

  @property({ type: String, attribute: 'dataset-id' }) datasetId = '';

  @state() private _dataset: Dataset | null = null;
  @state() private _preview: Preview | null = null;
  @state() private _isLoading = false;
  @state() private _error = '';

  override connectedCallback() {
    super.connectedCallback();
    if (this.datasetId) void this._load();
  }

  override updated(changed: Map<string, unknown>) {
    if (changed.has('datasetId') && this.datasetId) void this._load();
  }

  private async _load() {
    this._isLoading = true;
    this._error = '';
    try {
      // fetch dataset metadata and preview in parallel
      const [datasets, preview] = await Promise.all([
        listDatasets(),
        previewDataset(this.datasetId),
      ]);
      this._dataset = datasets.find((d) => d.id === this.datasetId) ?? null;
      this._preview = preview;
    } catch (error) {
      this._error = error instanceof Error ? error.message : 'Failed to load dataset';
    } finally {
      this._isLoading = false;
    }
  }

  render() {
    const ds = this._dataset;
    const preview = this._preview;
    return html`
      <bi-page-header heading=${ds?.name ?? 'Dataset'}>
        <a href="/datasets" slot="breadcrumb">← Datasets</a>
      </bi-page-header>

      ${this._isLoading ? html`<bi-spinner></bi-spinner>` : nothing}
      ${this._error ? html`<p class="error" role="alert">${this._error}</p>` : nothing}
      ${ds
        ? html`
            <bi-card heading="Schema">
              <table>
                <thead>
                  <tr>
                    <th>Column</th>
                    <th>Type</th>
                    <th>Nullable</th>
                  </tr>
                </thead>
                <tbody>
                  ${ds.columns.map(
                    (col) => html`
                      <tr>
                        <td>${col.name}</td>
                        <td>${col.dtype}</td>
                        <td>${col.nullable ? 'Yes' : 'No'}</td>
                      </tr>
                    `,
                  )}
                </tbody>
              </table>
            </bi-card>
          `
        : nothing}
      ${preview
        ? html`
            <bi-card heading="Preview">
              <table>
                <thead>
                  <tr>
                    ${preview.columns.map((col) => html`<th>${col}</th>`)}
                  </tr>
                </thead>
                <tbody>
                  ${preview.rows.map(
                    (row) => html`
                      <tr>
                        ${preview.columns.map((col) => html`<td>${cellStr(row[col])}</td>`)}
                      </tr>
                    `,
                  )}
                </tbody>
              </table>
            </bi-card>
          `
        : nothing}
    `;
  }
}

customElements.define('bi-dataset-detail', BiDatasetDetail);
