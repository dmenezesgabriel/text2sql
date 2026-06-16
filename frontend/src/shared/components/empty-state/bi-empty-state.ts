import { css, html, LitElement, nothing } from 'lit';
import { property } from 'lit/decorators.js';

export class BiEmptyState extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
    }
    .container {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: var(--spacing-2xl) var(--spacing-lg);
      gap: var(--spacing-md);
    }
    .icon {
      color: var(--color-border);
    }
    h3 {
      font-size: var(--text-md);
      font-weight: 600;
      color: var(--color-text);
      margin: 0;
    }
    p {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      margin: 0;
      max-width: 36ch;
    }
    .action {
      margin-top: var(--spacing-sm);
    }
  `;

  @property({ type: String }) heading = '';
  @property({ type: String }) description = '';

  connectedCallback() {
    super.connectedCallback();
    this.setAttribute('role', 'status');
    this.setAttribute('aria-live', 'polite');
  }

  render() {
    return html`
      <div class="container">
        <div class="icon">
          <slot name="icon"></slot>
        </div>
        <h3>${this.heading}</h3>
        ${this.description ? html`<p>${this.description}</p>` : nothing}
        <div class="action">
          <slot name="action"></slot>
        </div>
      </div>
    `;
  }
}

customElements.define('bi-empty-state', BiEmptyState);
