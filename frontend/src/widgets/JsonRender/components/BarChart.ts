import { Chart, registerables } from 'chart.js';
import { css,html, LitElement } from 'lit';
import { property } from 'lit/decorators.js';
import { createRef,ref } from 'lit/directives/ref.js';

Chart.register(...registerables);

export class BarChartElement extends LitElement {
  static styles = css`
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

  @property({ type: String }) title = '';
  @property({ type: String }) xAxis = '';
  @property({ type: String }) yAxis = '';
  @property({ type: Array }) data: { label: string; value: number }[] = [];
  @property({ type: String }) color = '#2563eb';

  private _chart: Chart | null = null;
  private _canvasRef = createRef<HTMLCanvasElement>();

  updated() {
    this._renderChart();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this._chart?.destroy();
  }

  private _renderChart() {
    const canvas = this._canvasRef.value;
    if (!canvas) return;
    this._chart?.destroy();

    this._chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: this.data.map((d) => d.label),
        datasets: [
          {
            label: this.title,
            data: this.data.map((d) => d.value),
            backgroundColor: this.color,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: !!this.title },
        },
        scales: {
          x: { title: { display: true, text: this.xAxis } },
          y: { title: { display: true, text: this.yAxis } },
        },
      },
    });
  }

  render() {
    return html`<canvas ${ref(this._canvasRef)}></canvas>`;
  }
}

customElements.define('bi-bar-chart', BarChartElement);
