import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'mono';

export class BiBadge extends LitElement {
  static readonly styles = css`
    :host {
      display: inline-flex;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-size: var(--text-xs);
      font-weight: 600;
      font-family: var(--font-sans);
      line-height: 1.5;
      white-space: nowrap;
    }
    .default {
      background: var(--color-bg-secondary);
      color: var(--color-text-secondary);
    }
    .primary {
      background: var(--color-primary-subtle);
      color: var(--color-primary);
    }
    /* Tints derived from the status color so they hold up in light and dark. */
    .success {
      background: color-mix(in srgb, var(--color-success) 14%, transparent);
      color: var(--color-success);
    }
    .warning {
      background: color-mix(in srgb, var(--color-warning) 16%, transparent);
      color: var(--color-warning);
    }
    .error {
      background: color-mix(in srgb, var(--color-error) 14%, transparent);
      color: var(--color-error);
    }
    .mono {
      font-family: var(--font-mono);
      font-size: var(--text-xs);
      background: var(--color-bg-secondary);
      color: var(--color-text-secondary);
    }
  `;

  @property({ type: String }) variant: BadgeVariant = 'default';

  render() {
    return html`<span class="badge ${this.variant}"><slot></slot></span>`;
  }
}

customElements.define('bi-badge', BiBadge);
