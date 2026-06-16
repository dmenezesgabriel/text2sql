import { css, html, LitElement, nothing } from 'lit';
import { property, state } from 'lit/decorators.js';

import type { AgentMessage } from '@/entities/agent/types';
import { createQuestion } from '@/features/question/api/question-api';
import { specToQuestionPayload } from '@/features/question/lib/spec-to-question-payload';
import { renderViz } from '@/widgets/json-render/render-viz';

/**
 *
 * @param saved
 * @param saving
 */
function parseSaveLabel(saved: boolean, saving: boolean): string {
  if (saved) return 'Saved ✓';
  if (saving) return 'Saving…';
  return 'Save as question';
}

export class BiChatMessage extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      padding: var(--spacing-xs) var(--spacing-md);
    }
    .user-row {
      display: flex;
      justify-content: flex-end;
    }
    .user-bubble {
      max-width: 70%;
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--radius-md);
      background: var(--color-primary);
      color: #fff;
      font-size: var(--text-sm);
      word-break: break-word;
    }
    .assistant-col {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    .thinking {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      font-style: italic;
      margin: 0;
    }
    .error {
      font-size: var(--text-sm);
      color: var(--color-error, #d32f2f);
      margin: 0;
    }
    .viz-wrap {
      max-width: 100%;
      overflow: auto;
    }
    .save-btn {
      align-self: flex-start;
      padding: var(--spacing-xs) var(--spacing-sm);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-sm);
      background: transparent;
      color: var(--color-text);
      font-size: var(--text-xs);
      font-family: inherit;
      cursor: pointer;
    }
    .save-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  `;

  @property({ type: Object }) message!: AgentMessage;

  @state() private _saved = false;
  @state() private _saving = false;

  private async _saveAsQuestion() {
    if (!this.message.spec || this._saved || this._saving) return;
    this._saving = true;
    try {
      const q = await createQuestion(specToQuestionPayload(this.message.spec));
      this._saved = true;
      this.dispatchEvent(
        new CustomEvent('question-saved', { detail: q, bubbles: true, composed: true }),
      );
    } catch {
      // saving failed — user can retry
    } finally {
      this._saving = false;
    }
  }

  private _renderAssistant() {
    const spec = this.message.spec;
    const component = spec ? (spec['component'] as string | undefined) : undefined;
    const props = (spec?.['props'] as Record<string, unknown> | undefined) ?? {};
    const hasContent = this.message.content.length > 0;
    const buttonLabel = parseSaveLabel(this._saved, this._saving);
    const contentClass = this.message.error ? 'error' : 'thinking';

    return html`
      <div class="assistant-col">
        ${hasContent ? html`<p class=${contentClass}>${this.message.content}</p>` : nothing}
        ${component
          ? html`
              <div class="viz-wrap">${renderViz(component, props)}</div>
              <button
                class="save-btn"
                ?disabled=${this._saved || this._saving}
                @click=${() => void this._saveAsQuestion()}
              >
                ${buttonLabel}
              </button>
            `
          : nothing}
      </div>
    `;
  }

  render() {
    if (this.message.role === 'user') {
      return html`
        <div class="user-row">
          <div class="user-bubble">${this.message.content}</div>
        </div>
      `;
    }
    return this._renderAssistant();
  }
}

customElements.define('bi-chat-message', BiChatMessage);
