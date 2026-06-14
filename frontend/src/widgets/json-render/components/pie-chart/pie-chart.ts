import type { ChartConfiguration } from 'chart.js';
import { property } from 'lit/decorators.js';

import { type CategoryDatum, ChartElement } from '../chart-element';

const PALETTE_TOKENS = ['--viz-1', '--viz-2', '--viz-3', '--viz-4', '--viz-5', '--viz-6'];
const PALETTE_FALLBACK = ['#5b63d3', '#e8794a', '#3aa675', '#d6477f', '#8a5cf6', '#d9a93a'];

export class PieChartElement extends ChartElement {
  @property({ type: String }) title = '';
  @property({ type: Array }) data: CategoryDatum[] = [];

  protected buildConfig(): ChartConfiguration {
    const tickColor = this.token('--color-text-secondary', '#79818d');
    const fontFamily = this.token('--font-sans', 'Inter, sans-serif');
    const colors = this.data.map((_, index) =>
      this.token(
        PALETTE_TOKENS[index % PALETTE_TOKENS.length] ?? '--viz-1',
        PALETTE_FALLBACK[index % PALETTE_FALLBACK.length] ?? '#5b63d3',
      ),
    );
    return {
      type: 'pie',
      data: {
        labels: this.data.map((d) => d.label),
        datasets: [{ data: this.data.map((d) => d.value), backgroundColor: colors }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
            labels: { color: tickColor, font: { family: fontFamily } },
          },
        },
      },
    };
  }
}

customElements.define('bi-pie-chart', PieChartElement);
