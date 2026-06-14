import type { ChartConfiguration } from 'chart.js';

import { CartesianChartElement } from '../cartesian-chart';

export class BarChartElement extends CartesianChartElement {
  protected buildConfig(): ChartConfiguration {
    const series = this.seriesColor();
    return this.cartesianConfig('bar', {
      backgroundColor: series,
      borderRadius: 3,
      maxBarThickness: 48,
    });
  }
}

customElements.define('bi-bar-chart', BarChartElement);
