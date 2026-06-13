import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

export class MetricElement extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      padding: 16px;
      border: 1px solid var(--color-border, #e0e0e0);
      border-radius: 8px;
      background: var(--color-bg, #ffffff);
    }
    .label {
      font-size: 12px;
      font-weight: 500;
      color: var(--color-text-secondary, #666);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .value {
      font-size: 28px;
      font-weight: 700;
      margin: 4px 0;
    }
    .change {
      font-size: 13px;
      font-weight: 500;
    }
    .change.up {
      color: var(--color-success, #16a34a);
    }
    .change.down {
      color: var(--color-error, #dc2626);
    }
    .change.neutral {
      color: var(--color-text-secondary, #666);
    }
  `;

  @property({ type: String }) label = '';
  @property({ type: String }) value = '';
  @property({ type: String }) change = '';
  @property({ type: String }) direction: 'up' | 'down' | 'neutral' = 'neutral';

  render() {
    return html`
      <div class="label">${this.label}</div>
      <div class="value">${this.value}</div>
      ${this.change ? html`<div class="change ${this.direction}">${this.change}</div>` : ''}
    `;
  }
}

customElements.define('bi-metric', MetricElement);
