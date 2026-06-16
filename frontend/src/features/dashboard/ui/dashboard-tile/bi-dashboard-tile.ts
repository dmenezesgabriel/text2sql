import { css, html, LitElement, nothing } from 'lit';
import { property } from 'lit/decorators.js';

export class BiDashboardTile extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
    }
    section {
      background: var(--color-bg);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
      padding: var(--spacing-md);
      height: 100%;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    :host([filtered]) section {
      border-left: 3px solid var(--color-primary);
    }
    .tile-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--spacing-sm);
    }
    h4 {
      font-size: var(--text-sm);
      font-weight: 600;
      color: var(--color-text);
      margin: 0;
    }
    .content {
      flex: 1;
      overflow: hidden;
    }
    .loading {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 120px;
    }
  `;

  @property({ type: String, attribute: 'tile-id' }) tileId = '';
  @property({ type: String }) heading = '';
  @property({ type: Number }) col = 1;
  @property({ type: Number }) width = 4;
  @property({ type: Number }) row = 1;
  @property({ type: Number }) height = 2;
  @property({ type: Boolean }) filtered = false;

  updated(changed: Map<string, unknown>) {
    if (changed.has('col') || changed.has('width') || changed.has('row') || changed.has('height')) {
      this._applyGridPlacement();
    }
  }

  connectedCallback() {
    super.connectedCallback();
    this._applyGridPlacement();
  }

  private _applyGridPlacement() {
    this.style.gridColumn = `${String(this.col)} / span ${String(this.width)}`;
    this.style.gridRow = `${String(this.row)} / span ${String(this.height)}`;
  }

  private _renderHeader() {
    if (!this.heading) {
      return html`
        <div class="loading">
          <bi-spinner size="md"></bi-spinner>
        </div>
      `;
    }
    const badge = this.filtered ? html`<bi-badge variant="primary">Filtered</bi-badge>` : nothing;
    return html`
      <div class="tile-header">
        <h4>${this.heading}</h4>
        ${badge}
      </div>
    `;
  }

  render() {
    const label = this.heading || 'Loading tile';

    return html`
      <section aria-label=${label}>
        ${this._renderHeader()}
        <div class="content">
          <slot></slot>
        </div>
      </section>
    `;
  }
}

customElements.define('bi-dashboard-tile', BiDashboardTile);
