import { css, html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';

const LINKS = [
  { href: '/chat', label: 'Chat' },
  { href: '/questions', label: 'Questions' },
  { href: '/dashboards', label: 'Dashboards' },
  { href: '/datasets', label: 'Datasets' },
] as const;

export class BiSidebar extends LitElement {
  static readonly styles = css`
    :host {
      display: flex;
      flex-direction: column;
      width: var(--sidebar-width, 200px);
      height: 100%;
      background: var(--color-bg-sidebar, var(--color-bg));
      border-right: 1px solid var(--color-border);
      flex-shrink: 0;
    }
    .logo {
      padding: var(--spacing-lg) var(--spacing-md);
      font-size: var(--text-xs);
      letter-spacing: 0.14em;
      font-weight: var(--weight-semibold);
      text-transform: uppercase;
      color: var(--color-primary);
      background-image:
        repeating-linear-gradient(
          0deg,
          transparent 0,
          transparent 23px,
          var(--color-grid-line, var(--color-border)) 24px
        ),
        repeating-linear-gradient(
          90deg,
          transparent 0,
          transparent 23px,
          var(--color-grid-line, var(--color-border)) 24px
        );
    }
    hr {
      border: none;
      border-top: 1px solid var(--color-border);
      margin: 0;
    }
    nav {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
      padding: var(--spacing-sm);
    }
    a {
      display: block;
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--radius-sm);
      font-size: var(--text-sm);
      text-decoration: none;
      color: var(--color-text-sidebar, var(--color-text-secondary));
      font-weight: 400;
    }
    a[aria-current='page'] {
      color: var(--color-text-sidebar-active, var(--color-text));
      background: var(--color-bg-sidebar-active, var(--color-bg-secondary));
      font-weight: 500;
    }
  `;

  @property({ type: String, attribute: 'active-href' }) activeHref = '';

  private _handleClick(href: string, e: Event) {
    e.preventDefault();
    this.dispatchEvent(
      new CustomEvent('navigate', { detail: href, bubbles: true, composed: true }),
    );
  }

  render() {
    return html`
      <div class="logo">text2sql</div>
      <hr aria-hidden="true" />
      <nav aria-label="Main navigation">
        ${LINKS.map(
          ({ href, label }) => html`
            <a
              href=${href}
              aria-current=${this.activeHref === href ? 'page' : 'false'}
              @click=${(e: Event) => {
                this._handleClick(href, e);
              }}
            >
              ${label}
            </a>
          `,
        )}
      </nav>
    `;
  }
}

customElements.define('bi-sidebar', BiSidebar);
