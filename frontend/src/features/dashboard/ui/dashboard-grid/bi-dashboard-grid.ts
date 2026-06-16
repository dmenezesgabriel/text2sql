import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

export class BiDashboardGrid extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
    }
    section {
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: var(--spacing-md);
      min-height: 200px;
    }
  `;

  @property({ type: String }) heading = '';

  render() {
    return html`
      <section aria-label=${this.heading || 'Dashboard'}>
        <slot></slot>
      </section>
    `;
  }
}

customElements.define('bi-dashboard-grid', BiDashboardGrid);
