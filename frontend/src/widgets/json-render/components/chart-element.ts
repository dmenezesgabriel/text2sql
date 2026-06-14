import { Chart, type ChartConfiguration, registerables } from 'chart.js';
import { css, html, LitElement } from 'lit';
import { createRef, type Ref, ref } from 'lit/directives/ref.js';

Chart.register(...registerables);

export interface CategoryDatum {
  label: string;
  value: number;
}

/**
 * Base for canvas charts: owns the canvas lifecycle and design-token
 * resolution, so each concrete chart only declares its Chart.js config.
 * Chart.js cannot read CSS `var()`, so `token()` resolves tokens to values.
 */
export abstract class ChartElement extends LitElement {
  static readonly styles = css`
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }
    canvas {
      width: 100% !important;
      height: 100% !important;
    }
  `;

  protected readonly canvasRef: Ref<HTMLCanvasElement> = createRef();
  private chart: Chart | null = null;

  protected token(name: string, fallback: string): string {
    const value = getComputedStyle(this).getPropertyValue(name).trim();
    return value || fallback;
  }

  protected abstract buildConfig(): ChartConfiguration;

  updated(): void {
    const canvas = this.canvasRef.value;
    if (!canvas) return;
    this.chart?.destroy();
    this.chart = new Chart(canvas, this.buildConfig());
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this.chart?.destroy();
  }

  render() {
    return html`<canvas ${ref(this.canvasRef)}></canvas>`;
  }
}
