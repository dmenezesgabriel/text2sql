import '@/shared/components/badge/bi-badge';
import '@/shared/components/card/bi-card';
import '@/shared/components/input/bi-input';
import '@/shared/components/page-header/bi-page-header';
import '@/shared/components/spinner/bi-spinner';

import { css, html, LitElement, nothing, type TemplateResult } from 'lit';
import { property, state } from 'lit/decorators.js';

import type { Question } from '@/entities/question/types';
import { deleteQuestion, drillQuestion, getQuestion } from '@/features/question/api/question-api';
import { renderViz } from '@/widgets/json-render/render-viz';

/**
 *
 * @param iso
 */
function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

export class BiQuestionDetail extends LitElement {
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
    pre {
      background: var(--color-bg-secondary);
      padding: var(--spacing-md);
      border-radius: var(--radius-sm);
      overflow-x: auto;
      margin: 0;
      font-size: var(--text-sm);
    }
    dl {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
      margin: 0;
    }
    .meta-row {
      display: flex;
      gap: var(--spacing-md);
    }
    dt {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      min-width: 80px;
    }
    dd {
      font-size: var(--text-sm);
      font-weight: 500;
      margin: 0;
    }
    .drill-fields {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    .drill-hint {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      margin: 0 0 var(--spacing-sm);
    }
    .drill-error {
      font-size: var(--text-xs);
      color: var(--color-error);
    }
  `;

  @property({ type: String, attribute: 'question-id' }) questionId = '';

  @state() private _question: Question | null = null;
  @state() private _isLoading = false;
  @state() private _error = '';
  @state() private _drillColumn = '';
  @state() private _drillValue = '';
  @state() private _isDrilling = false;
  @state() private _drillError = '';

  override connectedCallback() {
    super.connectedCallback();
    if (this.questionId) void this._load();
  }

  override updated(changed: Map<string, unknown>) {
    if (changed.has('questionId') && this.questionId) void this._load();
  }

  private async _load() {
    this._isLoading = true;
    this._error = '';
    try {
      this._question = await getQuestion(this.questionId);
    } catch (error) {
      this._error = error instanceof Error ? error.message : 'Failed to load question';
    } finally {
      this._isLoading = false;
    }
  }

  private async _handleDelete() {
    if (!this.questionId || !globalThis.confirm('Delete this question?')) return;
    try {
      await deleteQuestion(this.questionId);
      this.dispatchEvent(
        new CustomEvent('navigate', { detail: '/questions', bubbles: true, composed: true }),
      );
    } catch {
      // ignore
    }
  }

  private _drillLabel(): string {
    return this._isDrilling ? 'Drilling…' : 'Drill Down';
  }

  private _renderDrillError(): TemplateResult<1> {
    if (this._drillError) return html`<p class="drill-error">${this._drillError}</p>`;
    return html``;
  }

  private _metaValue(detail: string, isBadge: boolean) {
    if (isBadge) return html`<bi-badge variant="primary">${detail}</bi-badge>`;
    return html`${detail}`;
  }

  private async _handleDrill() {
    if (!this.questionId || !this._drillColumn.trim() || !this._drillValue.trim()) return;
    this._isDrilling = true;
    this._drillError = '';
    try {
      const result = await drillQuestion(this.questionId, {
        column: this._drillColumn.trim(),
        value: this._drillValue.trim(),
      });
      this.dispatchEvent(
        new CustomEvent('navigate', {
          detail: `/questions/${result.id}`,
          bubbles: true,
          composed: true,
        }),
      );
    } catch (error) {
      this._drillError = error instanceof Error ? error.message : 'Drill failed';
    } finally {
      this._isDrilling = false;
    }
  }

  render() {
    const q = this._question;
    return html`
      <bi-page-header heading=${q?.title ?? 'Question'}>
        <a href="/questions" slot="breadcrumb">← Questions</a>
        <button slot="actions" @click=${() => void this._handleDelete()}>Delete</button>
      </bi-page-header>

      ${this._isLoading ? html`<bi-spinner></bi-spinner>` : nothing}
      ${this._error ? html`<p class="error" role="alert">${this._error}</p>` : nothing}
      ${q
        ? html`
            <bi-card heading="Visualization"> ${renderViz(q.vizComponent, q.vizProps)} </bi-card>

            <bi-card heading="SQL Query">
              <pre><code>${q.sql}</code></pre>
            </bi-card>

            <bi-card heading="Metadata">
              <dl>
                ${(
                  [
                    ['Dataset', q.datasetId, false],
                    ['Format', q.vizFormat, true],
                    ['Created', formatDate(q.createdAt), false],
                    ['Updated', formatDate(q.updatedAt), false],
                  ] as [string, string, boolean][]
                ).map(
                  ([term, detail, isBadge]) => html`
                    <div class="meta-row">
                      <dt>${term}</dt>
                      <dd>${this._metaValue(detail, isBadge)}</dd>
                    </div>
                  `,
                )}
              </dl>
            </bi-card>

            <bi-card heading="Drill Down">
              <p class="drill-hint">Filter by a column value to create a derived question.</p>
              <div class="drill-fields">
                <bi-input
                  label="Column name"
                  .value=${this._drillColumn}
                  placeholder="e.g. region"
                  @bi-input-change=${(e: CustomEvent<string>) => {
                    this._drillColumn = e.detail;
                  }}
                ></bi-input>
                <bi-input
                  label="Filter value"
                  .value=${this._drillValue}
                  placeholder="e.g. North America"
                  @bi-input-change=${(e: CustomEvent<string>) => {
                    this._drillValue = e.detail;
                  }}
                ></bi-input>
                ${this._renderDrillError()}
                <button
                  ?disabled=${this._isDrilling ||
                  !this._drillColumn.trim() ||
                  !this._drillValue.trim()}
                  @click=${() => void this._handleDrill()}
                >
                  ${this._drillLabel()}
                </button>
              </div>
            </bi-card>
          `
        : nothing}
    `;
  }
}

customElements.define('bi-question-detail', BiQuestionDetail);
