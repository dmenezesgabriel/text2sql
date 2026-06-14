import { css, html, LitElement, nothing } from 'lit';
import { state } from 'lit/decorators.js';

import { registerS3Dataset } from '@/features/dataset/api/dataset-api';

export class BiRegisterDatasetForm extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
    }
    form {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    label {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: var(--text-sm);
      font-weight: 500;
      color: var(--color-text);
    }
    input {
      padding: var(--spacing-sm);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-sm);
      background: var(--color-surface);
      color: var(--color-text);
      font-size: var(--text-base);
      font-family: inherit;
    }
    input:disabled {
      opacity: 0.5;
    }
    .error {
      font-size: var(--text-sm);
      color: var(--color-error);
      margin: 0;
    }
    button[type='submit'] {
      align-self: flex-start;
      padding: var(--spacing-sm) var(--spacing-md);
      border: none;
      border-radius: var(--radius-sm);
      background: var(--color-primary);
      color: #fff;
      font-size: var(--text-sm);
      font-family: inherit;
      cursor: pointer;
    }
    button[type='submit']:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  `;

  @state() private _name = '';
  @state() private _s3Uri = '';
  @state() private _isLoading = false;
  @state() private _error = '';

  private readonly _handleSubmit = async (e: Event) => {
    e.preventDefault();
    if (!this._name.trim() || !this._s3Uri.trim()) return;
    this._isLoading = true;
    this._error = '';
    try {
      const dataset = await registerS3Dataset({
        name: this._name.trim(),
        s3_uri: this._s3Uri.trim(),
      });
      this._name = '';
      this._s3Uri = '';
      this.dispatchEvent(
        new CustomEvent('dataset-registered', { detail: dataset, bubbles: true, composed: true }),
      );
    } catch (error) {
      this._error = error instanceof Error ? error.message : 'Registration failed';
    } finally {
      this._isLoading = false;
    }
  };

  render() {
    const canSubmit = this._name.trim().length > 0 && this._s3Uri.trim().length > 0;
    return html`
      <form @submit=${this._handleSubmit}>
        <label>
          Name
          <input
            .value=${this._name}
            @input=${(e: InputEvent) => {
              this._name = (e.target as HTMLInputElement).value;
            }}
            placeholder="e.g. sales"
            ?disabled=${this._isLoading}
            required
          />
        </label>
        <label>
          S3 URI
          <input
            .value=${this._s3Uri}
            @input=${(e: InputEvent) => {
              this._s3Uri = (e.target as HTMLInputElement).value;
            }}
            placeholder="s3://bucket/path/file.parquet"
            ?disabled=${this._isLoading}
            required
          />
        </label>
        ${this._error ? html`<p class="error">${this._error}</p>` : nothing}
        <button type="submit" ?disabled=${this._isLoading || !canSubmit}>
          ${this._isLoading ? 'Registering…' : 'Register Dataset'}
        </button>
      </form>
    `;
  }
}

customElements.define('bi-register-dataset-form', BiRegisterDatasetForm);
