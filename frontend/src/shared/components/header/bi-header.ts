import { css, html, LitElement } from 'lit';

export class BiHeader extends LitElement {
  static readonly styles = css`
    :host {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-inline: var(--spacing-md);
      height: var(--header-height);
      flex-shrink: 0;
      border-bottom: 1px solid var(--color-border);
      background: var(--color-surface);
    }
    .title {
      font-size: var(--text-2xs);
      color: var(--color-text-secondary);
      letter-spacing: var(--tracking-caps);
      text-transform: uppercase;
      font-weight: var(--weight-semibold);
    }
    .actions {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
    }
  `;

  render() {
    return html`
      <span class="title">Generative BI</span>
      <div class="actions">
        <slot name="actions"></slot>
      </div>
    `;
  }
}

customElements.define('bi-header', BiHeader);
