import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

export class NarrativeTextElement extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      line-height: var(--leading-relaxed);
      font-size: var(--text-base);
      font-family: var(--font-sans);
      color: var(--color-text);
    }
    p {
      margin: 0 0 var(--spacing-sm) 0;
    }
    p:last-child {
      margin-bottom: 0;
    }
    .analytical {
      font-family: var(--font-mono);
      font-size: var(--text-sm);
    }
    .conversational {
      font-size: var(--text-md);
    }
    .executive {
      font-size: var(--text-base);
      font-weight: var(--weight-medium);
      letter-spacing: var(--tracking-tight);
    }
  `;

  @property({ type: String }) content = '';
  @property({ type: String }) tone: 'analytical' | 'conversational' | 'executive' =
    'conversational';

  render() {
    return html`
      <div class="${this.tone}">${this.content.split('\n').map((p) => html`<p>${p}</p>`)}</div>
    `;
  }
}

customElements.define('bi-narrative-text', NarrativeTextElement);
