import type { ChartConfiguration, ChartDataset } from 'chart.js';
import { property } from 'lit/decorators.js';

import { type CategoryDatum, ChartElement } from './chart-element';

type CartesianKind = 'bar' | 'line';

/**
 * Shared base for bar and line charts: both plot one numeric series across a
 * category/time axis, so the axis styling lives here and each subclass only
 * supplies its Chart.js type and dataset styling.
 */
export abstract class CartesianChartElement extends ChartElement {
  @property({ type: String }) title = '';
  @property({ type: String }) xAxis = '';
  @property({ type: String }) yAxis = '';
  @property({ type: Array }) data: CategoryDatum[] = [];
  @property({ type: String }) color = '';

  protected seriesColor(): string {
    return this.color || this.token('--viz-1', '#5b63d3');
  }

  protected cartesianConfig(
    kind: CartesianKind,
    dataset: Partial<ChartDataset<CartesianKind>>,
  ): ChartConfiguration {
    const gridColor = this.token('--color-grid-line', '#eceef1');
    const tickColor = this.token('--color-text-secondary', '#79818d');
    const fontFamily = this.token('--font-sans', 'Inter, sans-serif');
    const ticks = { color: tickColor, font: { family: fontFamily } };
    return {
      type: kind,
      data: {
        labels: this.data.map((d) => d.label),
        datasets: [{ label: this.title, data: this.data.map((d) => d.value), ...dataset }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: !!this.title, labels: ticks } },
        scales: {
          x: {
            title: { display: !!this.xAxis, text: this.xAxis, color: tickColor },
            ticks,
            grid: { display: false },
            border: { color: gridColor },
          },
          y: {
            title: { display: !!this.yAxis, text: this.yAxis, color: tickColor },
            ticks,
            grid: { color: gridColor },
            border: { display: false },
          },
        },
      },
    };
  }
}
