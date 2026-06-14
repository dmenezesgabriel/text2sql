import '@/features/dashboard/ui/dashboard-grid/bi-dashboard-grid';
import '@/features/dashboard/ui/dashboard-tile/bi-dashboard-tile';
import '@/shared/components/empty-state/bi-empty-state';
import '@/shared/components/page-header/bi-page-header';
import '@/shared/components/spinner/bi-spinner';

import { css, html, LitElement, nothing } from 'lit';
import { property, state } from 'lit/decorators.js';

import type { Dashboard } from '@/entities/dashboard/types';
import type { Question } from '@/entities/question/types';
import { getDashboard } from '@/features/dashboard/api/dashboard-api';
import { getQuestion } from '@/features/question/api/question-api';
import { renderViz } from '@/widgets/json-render/render-viz';

export class BiDashboardDetail extends LitElement {
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
  `;

  @property({ type: String, attribute: 'dashboard-id' }) dashboardId = '';

  @state() private _dashboard: Dashboard | null = null;
  @state() private _tileQuestions: Partial<Record<string, Question>> = {};
  @state() private _isLoading = false;
  @state() private _error = '';

  override connectedCallback() {
    super.connectedCallback();
    if (this.dashboardId) void this._load();
  }

  override updated(changed: Map<string, unknown>) {
    if (changed.has('dashboardId') && this.dashboardId) void this._load();
  }

  private async _load() {
    this._isLoading = true;
    this._error = '';
    try {
      const dashboard = await getDashboard(this.dashboardId);
      this._dashboard = dashboard;

      if (dashboard.tiles.length > 0) {
        const pairs = await Promise.all(
          dashboard.tiles.map((tile) =>
            getQuestion(tile.questionId).then((q) => [tile.questionId, q] as const),
          ),
        );
        this._tileQuestions = Object.fromEntries(pairs);
      }
    } catch (error) {
      this._error = error instanceof Error ? error.message : 'Failed to load dashboard';
    } finally {
      this._isLoading = false;
    }
  }

  render() {
    const db = this._dashboard;
    return html`
      <bi-page-header heading=${db?.title ?? 'Dashboard'}>
        <a href="/dashboards" slot="breadcrumb">← Dashboards</a>
      </bi-page-header>

      ${this._isLoading ? html`<bi-spinner></bi-spinner>` : nothing}
      ${this._error ? html`<p class="error" role="alert">${this._error}</p>` : nothing}
      ${db && db.tiles.length === 0
        ? html`
            <bi-empty-state
              heading="No tiles"
              description="Save questions from Chat and add them to this dashboard."
            ></bi-empty-state>
          `
        : nothing}
      ${db && db.tiles.length > 0
        ? html`
            <bi-dashboard-grid heading=${db.title}>
              ${db.tiles.map((tile) => {
                const q = this._tileQuestions[tile.questionId] ?? null;
                return html`
                  <bi-dashboard-tile
                    tile-id=${tile.id}
                    heading=${q?.title ?? ''}
                    col=${tile.position.col}
                    width=${tile.position.width}
                    row=${tile.position.row}
                    height=${tile.position.height}
                  >
                    ${q ? renderViz(q.vizComponent, q.vizProps) : html`<bi-spinner></bi-spinner>`}
                  </bi-dashboard-tile>
                `;
              })}
            </bi-dashboard-grid>
          `
        : nothing}
    `;
  }
}

customElements.define('bi-dashboard-detail', BiDashboardDetail);
