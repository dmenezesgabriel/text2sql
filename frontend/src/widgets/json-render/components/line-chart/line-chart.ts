import type { ChartConfiguration } from 'chart.js';

import { CartesianChartElement } from '../cartesian-chart';

export class LineChartElement extends CartesianChartElement {
  protected buildConfig(): ChartConfiguration {
    const series = this.seriesColor();
    return this.cartesianConfig('line', {
      borderColor: series,
      backgroundColor: series,
      pointRadius: 3,
      tension: 0.35,
      fill: false,
    });
  }
}

customElements.define('bi-line-chart', LineChartElement);
