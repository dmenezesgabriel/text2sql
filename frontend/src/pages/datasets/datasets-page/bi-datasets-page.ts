import '@/features/dataset/ui/register-dataset-form/bi-register-dataset-form';
import '@/shared/components/card/bi-card';
import '@/shared/components/empty-state/bi-empty-state';
import '@/shared/components/page-header/bi-page-header';
import '@/shared/components/spinner/bi-spinner';

import { css, html, LitElement, nothing } from 'lit';
import { state } from 'lit/decorators.js';

import type { Dataset } from '@/entities/dataset/types';
import { deleteDataset, listDatasets } from '@/features/dataset/api/dataset-api';

export class BiDatasetsPage extends LitElement {
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
    }
    th,
    td {
      text-align: left;
      padding: var(--spacing-sm) var(--spacing-md);
      border-bottom: 1px solid var(--color-border);
    }
    th {
      font-weight: 600;
      color: var(--color-text-secondary);
    }
    a {
      color: var(--color-primary);
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
    button.del {
      padding: 2px var(--spacing-sm);
      border: 1px solid var(--color-error);
      border-radius: var(--radius-sm);
      background: transparent;
      color: var(--color-error);
      font-size: var(--text-xs);
      cursor: pointer;
      font-family: inherit;
    }
  `;

  @state() private _datasets: Dataset[] = [];
  @state() private _isLoading = false;
  @state() private _error = '';

  override connectedCallback() {
    super.connectedCallback();
    void this._load();
  }

  private async _load() {
    this._isLoading = true;
    this._error = '';
    try {
      this._datasets = await listDatasets();
    } catch (error) {
      this._error = error instanceof Error ? error.message : 'Failed to load datasets';
    } finally {
      this._isLoading = false;
    }
  }

  private _handleRegistered(e: CustomEvent<Dataset>) {
    this._datasets = [...this._datasets, e.detail];
  }

  private async _handleDelete(id: string) {
    if (!globalThis.confirm('Delete this dataset?')) return;
    try {
      await deleteDataset(id);
      this._datasets = this._datasets.filter((d) => d.id !== id);
    } catch {
      // ignore
    }
  }

  render() {
    return html`
      <bi-page-header heading="Datasets"></bi-page-header>

      <bi-card heading="Register S3 Dataset">
        <bi-register-dataset-form
          @dataset-registered=${(e: CustomEvent<Dataset>) => {
            this._handleRegistered(e);
          }}
        ></bi-register-dataset-form>
      </bi-card>

      ${this._isLoading ? html`<bi-spinner></bi-spinner>` : nothing}
      ${this._error ? html`<p class="error" role="alert">${this._error}</p>` : nothing}
      ${!this._isLoading && this._datasets.length === 0 && !this._error
        ? html`
            <bi-empty-state
              heading="No datasets"
              description="Register an S3 dataset above to get started."
            ></bi-empty-state>
          `
        : nothing}
      ${this._datasets.length > 0
        ? html`
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Kind</th>
                  <th>Columns</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                ${this._datasets.map(
                  (d) => html`
                    <tr>
                      <td><a href="/datasets/${d.id}">${d.name}</a></td>
                      <td>${d.kind}</td>
                      <td>${d.columns.length}</td>
                      <td>
                        <button class="del" @click=${() => this._handleDelete(d.id)}>Delete</button>
                      </td>
                    </tr>
                  `,
                )}
              </tbody>
            </table>
          `
        : nothing}
    `;
  }
}

customElements.define('bi-datasets-page', BiDatasetsPage);
