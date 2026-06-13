import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

export class NarrativeTextElement extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      line-height: 1.6;
      font-size: 15px;
      color: var(--color-text, #1a1a1a);
    }
    p {
      margin: 0 0 12px 0;
    }
    .analytical {
      font-family: var(--font-mono, monospace);
    }
    .conversational {
      font-size: 16px;
    }
    .executive {
      font-size: 14px;
      font-weight: 500;
      letter-spacing: 0.01em;
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
