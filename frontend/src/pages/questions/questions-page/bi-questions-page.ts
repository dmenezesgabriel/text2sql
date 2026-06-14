import '@/features/question/ui/question-card/bi-question-card';
import '@/shared/components/empty-state/bi-empty-state';
import '@/shared/components/page-header/bi-page-header';
import '@/shared/components/spinner/bi-spinner';

import { css, html, LitElement, nothing } from 'lit';
import { state } from 'lit/decorators.js';

import type { Question } from '@/entities/question/types';
import { deleteQuestion, listQuestions } from '@/features/question/api/question-api';

export class BiQuestionsPage extends LitElement {
  static readonly styles = css`
    :host {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-lg);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: var(--spacing-md);
    }
    .error {
      font-size: var(--text-sm);
      color: var(--color-error);
    }
  `;

  @state() private _questions: Question[] = [];
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
      this._questions = await listQuestions();
    } catch (error) {
      this._error = error instanceof Error ? error.message : 'Failed to load questions';
    } finally {
      this._isLoading = false;
    }
  }

  private async _handleDelete(e: CustomEvent<string>) {
    const id = e.detail;
    try {
      await deleteQuestion(id);
      this._questions = this._questions.filter((q) => q.id !== id);
    } catch {
      // ignore — card stays in place
    }
  }

  render() {
    return html`
      <bi-page-header heading="Questions"></bi-page-header>
      ${this._isLoading ? html`<bi-spinner></bi-spinner>` : nothing}
      ${this._error ? html`<p class="error" role="alert">${this._error}</p>` : nothing}
      ${!this._isLoading && this._questions.length === 0 && !this._error
        ? html`
            <bi-empty-state
              heading="No questions yet"
              description="Ask a question in Chat to create your first saved question."
            ></bi-empty-state>
          `
        : nothing}
      ${this._questions.length > 0
        ? html`
            <div class="grid">
              ${this._questions.map(
                (q) => html`
                  <bi-question-card
                    question-id=${q.id}
                    title=${q.title}
                    viz-format=${q.vizFormat}
                    sql=${q.sql}
                    created-at=${q.createdAt}
                    show-delete
                    @bi-question-delete=${(e: CustomEvent<string>) => void this._handleDelete(e)}
                  ></bi-question-card>
                `,
              )}
            </div>
          `
        : nothing}
    `;
  }
}

customElements.define('bi-questions-page', BiQuestionsPage);
