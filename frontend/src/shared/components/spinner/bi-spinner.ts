import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

type SpinnerSize = 'sm' | 'md' | 'lg';

const sizeMap: Record<SpinnerSize, string> = {
  sm: '16px',
  md: '24px',
  lg: '36px',
};

export class BiSpinner extends LitElement {
  static readonly styles = css`
    :host {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--spacing-xl);
    }
    .ring {
      border-radius: 50%;
      border: 2px solid var(--color-border);
      border-top-color: var(--color-primary);
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  `;

  @property({ type: String }) size: SpinnerSize = 'md';

  connectedCallback() {
    super.connectedCallback();
    this.setAttribute('role', 'status');
    this.setAttribute('aria-label', 'Loading');
  }

  render() {
    const dim = sizeMap[this.size];
    return html` <div class="ring" style="width:${dim};height:${dim};"></div> `;
  }
}

customElements.define('bi-spinner', BiSpinner);
