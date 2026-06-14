import '@/shared/components/card/bi-card';
import '@/shared/components/empty-state/bi-empty-state';
import '@/shared/components/page-header/bi-page-header';
import '@/shared/components/spinner/bi-spinner';

import { css, html, LitElement, nothing } from 'lit';
import { state } from 'lit/decorators.js';

import type { Dashboard } from '@/entities/dashboard/types';
import {
  createDashboard,
  deleteDashboard,
  listDashboards,
} from '@/features/dashboard/api/dashboard-api';

export class BiDashboardsPage extends LitElement {
  static readonly styles = css`
    :host {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-lg);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: var(--spacing-md);
    }
    .card-body {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    time {
      font-size: var(--text-xs);
      color: var(--color-text-secondary);
    }
    a.view-link {
      display: inline-flex;
      align-items: center;
      padding: 4px var(--spacing-sm);
      font-size: var(--text-xs);
      font-weight: 500;
      color: var(--color-text-secondary);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-sm);
      text-decoration: none;
    }
    a.view-link:hover {
      background: var(--color-bg-secondary);
    }
    button.del {
      padding: 4px var(--spacing-sm);
      border: 1px solid var(--color-error);
      border-radius: var(--radius-sm);
      background: transparent;
      color: var(--color-error);
      font-size: var(--text-xs);
      cursor: pointer;
      font-family: inherit;
    }
    .actions-row {
      display: flex;
      gap: var(--spacing-xs);
      margin-top: auto;
    }
    .error {
      font-size: var(--text-sm);
      color: var(--color-error);
    }
  `;

  @state() private _dashboards: Dashboard[] = [];
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
      this._dashboards = await listDashboards();
    } catch (error) {
      this._error = error instanceof Error ? error.message : 'Failed to load dashboards';
    } finally {
      this._isLoading = false;
    }
  }

  private async _handleCreate() {
    const title = globalThis.prompt('Dashboard title');
    if (!title?.trim()) return;
    try {
      const dashboard = await createDashboard({ title: title.trim() });
      this.dispatchEvent(
        new CustomEvent('navigate', {
          detail: `/dashboards/${dashboard.id}`,
          bubbles: true,
          composed: true,
        }),
      );
    } catch {
      // ignore
    }
  }

  private async _handleDelete(id: string) {
    if (!globalThis.confirm('Delete this dashboard?')) return;
    try {
      await deleteDashboard(id);
      this._dashboards = this._dashboards.filter((d) => d.id !== id);
    } catch {
      // ignore
    }
  }

  render() {
    return html`
      <bi-page-header heading="Dashboards">
        <button slot="actions" @click=${() => void this._handleCreate()}>+ New Dashboard</button>
      </bi-page-header>

      ${this._isLoading ? html`<bi-spinner></bi-spinner>` : nothing}
      ${this._error ? html`<p class="error" role="alert">${this._error}</p>` : nothing}
      ${!this._isLoading && this._dashboards.length === 0 && !this._error
        ? html`
            <bi-empty-state
              heading="No dashboards yet"
              description="Create a dashboard to arrange your saved questions."
            ></bi-empty-state>
          `
        : nothing}
      ${this._dashboards.length > 0
        ? html`
            <div class="grid">
              ${this._dashboards.map(
                (d) => html`
                  <bi-card heading=${d.title}>
                    <div class="card-body">
                      <time datetime=${d.createdAt}>
                        ${new Date(d.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </time>
                      <div class="actions-row">
                        <a class="view-link" href="/dashboards/${d.id}">View</a>
                        <button class="del" @click=${() => this._handleDelete(d.id)}>Delete</button>
                      </div>
                    </div>
                  </bi-card>
                `,
              )}
            </div>
          `
        : nothing}
    `;
  }
}

customElements.define('bi-dashboards-page', BiDashboardsPage);
