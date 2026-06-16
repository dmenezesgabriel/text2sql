import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

export class MetricElement extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      padding: var(--spacing-md);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      background: var(--color-surface);
      color: var(--color-text);
    }
    .label {
      font-size: var(--text-2xs);
      font-weight: var(--weight-semibold);
      color: var(--color-text-secondary);
      text-transform: uppercase;
      letter-spacing: var(--tracking-caps);
    }
    /* The number is the point: large, tight, tabular so it reads as data. */
    .value {
      font-size: var(--text-2xl);
      font-weight: var(--weight-semibold);
      line-height: var(--leading-tight);
      letter-spacing: var(--tracking-tight);
      font-variant-numeric: tabular-nums;
      margin: var(--spacing-xs) 0;
    }
    .change {
      font-size: var(--text-sm);
      font-weight: var(--weight-medium);
      font-variant-numeric: tabular-nums;
    }
    .change.up {
      color: var(--color-success);
    }
    .change.down {
      color: var(--color-error);
    }
    .change.neutral {
      color: var(--color-text-secondary);
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
