import { css, html, LitElement } from 'lit';
import { property, state } from 'lit/decorators.js';

export class BiChatInput extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
    }
    form {
      display: flex;
      gap: var(--spacing-sm);
      padding: var(--spacing-md);
      border-top: 1px solid var(--color-border);
      background: var(--color-bg);
    }
    input {
      flex: 1;
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--radius-sm);
      border: 1px solid var(--color-border);
      background: var(--color-surface);
      color: var(--color-text);
      font-size: var(--text-base);
      font-family: inherit;
      outline: none;
    }
    input:focus {
      border-color: var(--color-primary);
    }
    button[type='submit'] {
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--radius-sm);
      border: none;
      background: var(--color-primary);
      color: #ffffff;
      font-size: var(--text-base);
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
    }
    button[type='submit']:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  `;

  @property({ type: Boolean }) disabled = false;

  @state() private _value = '';

  private _handleSubmit(e: Event) {
    e.preventDefault();
    const trimmed = this._value.trim();
    if (!trimmed || this.disabled) return;
    this.dispatchEvent(new CustomEvent('send', { detail: trimmed, bubbles: true, composed: true }));
    this._value = '';
  }

  render() {
    return html`
      <form
        @submit=${(e: Event) => {
          this._handleSubmit(e);
        }}
      >
        <input
          .value=${this._value}
          @input=${(e: InputEvent) => {
            this._value = (e.target as HTMLInputElement).value;
          }}
          placeholder="Ask a question about your data..."
          ?disabled=${this.disabled}
        />
        <button type="submit" ?disabled=${this.disabled || !this._value.trim()}>Send</button>
      </form>
    `;
  }
}

customElements.define('bi-chat-input', BiChatInput);
