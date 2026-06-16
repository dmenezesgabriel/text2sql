import { css, html, LitElement, nothing } from 'lit';
import { property } from 'lit/decorators.js';

export class BiQuestionCard extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
    }
    article {
      background: var(--color-bg);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
      padding: var(--spacing-lg);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
      height: 100%;
      box-sizing: border-box;
      transition: box-shadow 0.15s;
    }
    article:hover {
      box-shadow: var(--shadow-md);
    }
    .header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--spacing-sm);
    }
    h3 {
      font-size: var(--text-base);
      font-weight: 600;
      color: var(--color-text);
      margin: 0;
      flex: 1;
    }
    h3 a {
      color: inherit;
      text-decoration: none;
    }
    h3 a:hover {
      color: var(--color-primary);
    }
    time {
      font-size: var(--text-xs);
      color: var(--color-text-secondary);
      font-variant-numeric: tabular-nums;
    }
    .sql-preview {
      font-family: var(--font-mono);
      font-size: var(--text-xs);
      color: var(--color-text-secondary);
      background: var(--color-bg-secondary);
      padding: var(--spacing-sm);
      border-radius: var(--radius-sm);
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .actions {
      display: flex;
      gap: var(--spacing-xs);
      margin-top: auto;
      padding-top: var(--spacing-sm);
    }
    a.view-link {
      display: inline-flex;
      align-items: center;
      padding: 4px var(--spacing-sm);
      font-size: var(--text-xs);
      font-weight: 500;
      color: var(--color-text-secondary);
      text-decoration: none;
      border-radius: var(--radius-sm);
      border: 1px solid var(--color-border);
    }
    a.view-link:hover {
      background: var(--color-bg-secondary);
      color: var(--color-text);
    }
    button.delete-btn {
      display: inline-flex;
      align-items: center;
      padding: 4px var(--spacing-sm);
      font-size: var(--text-xs);
      font-weight: 500;
      color: var(--color-error);
      background: transparent;
      border: 1px solid var(--color-error);
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-family: var(--font-sans);
    }
    button.delete-btn:hover {
      background: #fee2e2;
    }
  `;

  @property({ type: String, attribute: 'question-id' }) questionId = '';
  @property({ type: String }) title = '';
  @property({ type: String, attribute: 'viz-format' }) vizFormat = '';
  @property({ type: String }) sql = '';
  @property({ type: String, attribute: 'created-at' }) createdAt = '';
  @property({ type: Boolean, attribute: 'show-delete' }) showDelete = false;

  private _formatDate(iso: string): string {
    if (!iso) return '';
    try {
      return new Date(iso).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return iso;
    }
  }

  private _onDelete() {
    this.dispatchEvent(
      new CustomEvent('bi-question-delete', {
        detail: this.questionId,
        bubbles: true,
        composed: true,
      }),
    );
  }

  render() {
    const sqlPreview = this.sql.length > 80 ? `${this.sql.slice(0, 80)}…` : this.sql;

    return html`
      <article aria-label=${this.title}>
        <div class="header">
          <h3>
            <a href="/questions/${this.questionId}">${this.title}</a>
          </h3>
          <bi-badge variant="primary">${this.vizFormat}</bi-badge>
        </div>
        <time datetime=${this.createdAt}>${this._formatDate(this.createdAt)}</time>
        ${this.sql ? html`<code class="sql-preview">${sqlPreview}</code>` : nothing}
        <div class="actions">
          <a class="view-link" href="/questions/${this.questionId}">View</a>
          ${this.showDelete
            ? html`<button
                class="delete-btn"
                @click=${() => {
                  this._onDelete();
                }}
              >
                Delete
              </button>`
            : nothing}
        </div>
      </article>
    `;
  }
}

customElements.define('bi-question-card', BiQuestionCard);
