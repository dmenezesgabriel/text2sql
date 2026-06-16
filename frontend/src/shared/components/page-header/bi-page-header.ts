import { css, html, LitElement, nothing } from 'lit';
import { property } from 'lit/decorators.js';

export class BiPageHeader extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      margin-bottom: var(--spacing-lg);
    }
    .root {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--spacing-md);
    }
    .left {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
    }
    .breadcrumb {
      font-size: var(--text-xs);
      color: var(--color-text-secondary);
    }
    h1 {
      font-size: var(--text-xl);
      font-weight: 700;
      color: var(--color-text);
      margin: 0;
    }
    p {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      margin: 0;
    }
    .actions {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      flex-shrink: 0;
    }
  `;

  @property({ type: String }) heading = '';
  @property({ type: String }) description = '';

  render() {
    return html`
      <div class="root">
        <div class="left">
          <div class="breadcrumb">
            <slot name="breadcrumb"></slot>
          </div>
          <hgroup>
            <h1>${this.heading}</h1>
            ${this.description ? html`<p>${this.description}</p>` : nothing}
          </hgroup>
        </div>
        <div class="actions">
          <slot name="actions"></slot>
        </div>
      </div>
    `;
  }
}

customElements.define('bi-page-header', BiPageHeader);
