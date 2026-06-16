import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md';
type ButtonType = 'button' | 'submit' | 'reset';

export class BiButton extends LitElement {
  static readonly styles = css`
    :host {
      display: inline-flex;
    }
    button {
      display: inline-flex;
      align-items: center;
      gap: var(--spacing-xs);
      border-radius: var(--radius-sm);
      font-family: var(--font-sans);
      font-weight: var(--weight-medium);
      cursor: pointer;
      transition:
        background-color 0.12s ease,
        opacity 0.12s ease;
      white-space: nowrap;
    }
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    :host(:focus-visible) button {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }

    /* Sizes */
    .sm {
      padding: 4px var(--spacing-sm);
      font-size: var(--text-xs);
    }
    .md {
      padding: var(--spacing-sm) var(--spacing-md);
      font-size: var(--text-base);
    }

    /* Variants */
    .primary {
      background: var(--color-primary);
      color: #fff;
      border: none;
    }
    .primary:hover:not(:disabled) {
      background: var(--color-primary-hover);
    }
    .secondary {
      background: var(--color-surface);
      color: var(--color-text);
      border: 1px solid var(--color-border);
    }
    .secondary:hover:not(:disabled) {
      background: var(--color-bg-secondary);
      border-color: var(--color-border-strong);
    }
    .ghost {
      background: transparent;
      color: var(--color-text-secondary);
      border: none;
    }
    .ghost:hover:not(:disabled) {
      color: var(--color-text);
      background: var(--color-bg-secondary);
    }
    .danger {
      background: var(--color-error);
      color: #fff;
      border: none;
    }
    .danger:hover:not(:disabled) {
      opacity: 0.85;
    }
  `;

  @property({ type: String }) variant: ButtonVariant = 'secondary';
  @property({ type: String }) size: ButtonSize = 'md';
  @property({ type: Boolean }) disabled = false;
  @property({ type: String }) type: ButtonType = 'button';

  render() {
    return html`
      <button
        type=${this.type}
        ?disabled=${this.disabled}
        aria-disabled=${this.disabled ? 'true' : 'false'}
        class="${this.variant} ${this.size}"
      >
        <slot></slot>
      </button>
    `;
  }
}

customElements.define('bi-button', BiButton);
