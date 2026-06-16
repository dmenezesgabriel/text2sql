import '../header/bi-header';
import '../sidebar/bi-sidebar';

import { css, html, LitElement } from 'lit';

export class BiLayout extends LitElement {
  static readonly styles = css`
    :host {
      display: flex;
      height: 100vh;
      overflow: hidden;
    }
    .body {
      display: flex;
      flex-direction: column;
      flex: 1;
      overflow: hidden;
    }
    main {
      flex: 1;
      overflow: auto;
      padding: var(--spacing-lg);
    }
    a.skip-nav {
      position: absolute;
      top: -999px;
      left: -999px;
    }
    a.skip-nav:focus {
      top: var(--spacing-sm);
      left: var(--spacing-sm);
      z-index: 100;
    }
  `;

  render() {
    return html`
      <a class="skip-nav" href="#main-content">Skip to content</a>
      <bi-sidebar></bi-sidebar>
      <div class="body">
        <bi-header>
          <slot name="header-actions" slot="actions"></slot>
        </bi-header>
        <main id="main-content">
          <slot></slot>
        </main>
      </div>
    `;
  }
}

customElements.define('bi-layout', BiLayout);
