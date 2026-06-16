import { css, html, LitElement, nothing } from 'lit';
import { property } from 'lit/decorators.js';

type CardPadding = 'sm' | 'md' | 'lg';

const paddingMap: Record<CardPadding, string> = {
  sm: 'var(--spacing-sm)',
  md: 'var(--spacing-md)',
  lg: 'var(--spacing-lg)',
};

export class BiCard extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
    }
    article {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
    }
    h3 {
      font-size: var(--text-md);
      font-weight: var(--weight-semibold);
      letter-spacing: var(--tracking-tight);
      color: var(--color-text);
      margin: 0 0 var(--spacing-md) 0;
    }
    .footer {
      border-top: 1px solid var(--color-border);
      margin-top: var(--spacing-md);
      padding-top: var(--spacing-md);
    }
    ::slotted(*) {
      box-sizing: border-box;
    }
  `;

  @property({ type: String }) heading = '';
  @property({ type: String }) padding: CardPadding = 'lg';

  render() {
    const pad = paddingMap[this.padding];
    const labelledBy = this.heading ? 'card-heading' : nothing;

    return html`
      <article aria-labelledby=${labelledBy} style="padding:${pad}">
        ${this.heading ? html`<h3 id="card-heading">${this.heading}</h3>` : nothing}
        <slot></slot>
        <div class="footer" style="display:none">
          <slot
            name="footer"
            @slotchange=${(e: Event) => {
              this._onFooterSlotChange(e);
            }}
          ></slot>
        </div>
      </article>
    `;
  }

  private _onFooterSlotChange(e: Event) {
    const slot = e.target as HTMLSlotElement;
    const footer = slot.closest<HTMLElement>('.footer');
    if (footer) {
      footer.style.display = slot.assignedElements().length > 0 ? 'block' : 'none';
    }
  }
}

customElements.define('bi-card', BiCard);
