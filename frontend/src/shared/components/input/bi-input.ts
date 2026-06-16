import { css, html, LitElement, nothing } from 'lit';
import { property, state } from 'lit/decorators.js';

type InputType = 'text' | 'email' | 'search' | 'url';

export class BiInput extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
    }
    .field {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    label {
      font-size: var(--text-sm);
      font-weight: 500;
      color: var(--color-text);
    }
    .required {
      color: var(--color-error);
      margin-left: 2px;
    }
    input {
      width: 100%;
      padding: var(--spacing-sm) var(--spacing-md);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-sm);
      font-size: var(--text-base);
      font-family: var(--font-sans);
      background: var(--color-surface);
      color: var(--color-text);
      box-sizing: border-box;
      transition:
        border-color 0.15s,
        box-shadow 0.15s;
    }
    input::placeholder {
      color: var(--color-text-tertiary);
    }
    input:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px var(--color-primary-subtle);
    }
    input.has-error {
      border-color: var(--color-error);
    }
    input:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      background: var(--color-bg-secondary);
    }
    .hint {
      font-size: var(--text-xs);
      color: var(--color-text-secondary);
    }
    .error-msg {
      font-size: var(--text-xs);
      color: var(--color-error);
    }
  `;

  @property({ type: String }) label = '';
  @property({ type: String }) value = '';
  @property({ type: String }) placeholder = '';
  @property({ type: Boolean }) disabled = false;
  @property({ type: String }) error = '';
  @property({ type: String }) hint = '';
  @property({ type: String }) type: InputType = 'text';
  @property({ type: Boolean }) required = false;

  @state() private _uid = `bi-input-${crypto.randomUUID().slice(0, 8)}`;

  private _onInput(e: Event) {
    const target = e.target as HTMLInputElement;
    this.value = target.value;
    this.dispatchEvent(
      new CustomEvent('bi-input-change', {
        detail: target.value,
        bubbles: true,
        composed: true,
      }),
    );
  }

  /** @returns the label template, or nothing when unset */
  private _renderLabel() {
    if (!this.label) return nothing;
    const requiredMark = this.required
      ? html`<span class="required" aria-hidden="true">*</span>`
      : nothing;
    return html` <label for=${this._uid}> ${this.label} ${requiredMark} </label> `;
  }

  /** @returns the id of the element describing this input, or nothing when unset */
  private _renderDescribedBy() {
    if (this.error) return `${this._uid}-error`;
    if (this.hint) return `${this._uid}-hint`;
    return nothing;
  }

  /** @returns the error or hint template, or nothing when neither is set */
  private _renderHelpText() {
    if (this.error) {
      return html`<span id="${this._uid}-error" class="error-msg">${this.error}</span>`;
    }
    if (this.hint) {
      return html`<span id="${this._uid}-hint" class="hint">${this.hint}</span>`;
    }
    return nothing;
  }

  render() {
    return html`
      <div class="field">
        ${this._renderLabel()}
        <input
          id=${this._uid}
          type=${this.type}
          .value=${this.value}
          placeholder=${this.placeholder}
          ?disabled=${this.disabled}
          ?required=${this.required}
          aria-invalid=${this.error ? 'true' : 'false'}
          aria-describedby=${this._renderDescribedBy()}
          class=${this.error ? 'has-error' : ''}
          @input=${(e: Event) => {
            this._onInput(e);
          }}
        />
        ${this._renderHelpText()}
      </div>
    `;
  }
}

customElements.define('bi-input', BiInput);
