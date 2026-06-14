import './components/bar-chart/bar-chart';
import './components/data-table/data-table';
import './components/line-chart/line-chart';
import './components/metric/metric';
import './components/narrative-text/narrative-text';
import './components/pie-chart/pie-chart';

import { html, nothing, type TemplateResult } from 'lit';

type VizTemplate = TemplateResult<1> | typeof nothing;

/**
 * Renders a visualization component template.
 * @param component - Component name (e.g., 'BarChart', 'DataTable')
 * @param props - Component props object
 * @returns Lit template or nothing if component not found
 */
export function renderViz(component: string, props: Record<string, unknown>): VizTemplate {
  if (component === 'BarChart') {
    return html`
      <bi-bar-chart
        title=${props['title'] ?? ''}
        .xAxis=${props['xAxis'] ?? ''}
        .yAxis=${props['yAxis'] ?? ''}
        .data=${props['data'] ?? []}
        .color=${props['color'] ?? ''}
      ></bi-bar-chart>
    `;
  }
  if (component === 'LineChart') {
    return html`
      <bi-line-chart
        title=${props['title'] ?? ''}
        .xAxis=${props['xAxis'] ?? ''}
        .yAxis=${props['yAxis'] ?? ''}
        .data=${props['data'] ?? []}
      ></bi-line-chart>
    `;
  }
  if (component === 'PieChart') {
    return html`
      <bi-pie-chart title=${props['title'] ?? ''} .data=${props['data'] ?? []}></bi-pie-chart>
    `;
  }
  if (component === 'DataTable') {
    return html`
      <bi-data-table
        title=${props['title'] ?? ''}
        .columns=${props['columns'] ?? []}
        .rows=${props['rows'] ?? []}
      ></bi-data-table>
    `;
  }
  if (component === 'Metric') {
    return html`
      <bi-metric
        label=${props['label'] ?? ''}
        value=${props['value'] ?? ''}
        change=${props['change'] ?? ''}
        direction=${props['direction'] ?? 'neutral'}
      ></bi-metric>
    `;
  }
  if (component === 'NarrativeText') {
    return html`
      <bi-narrative-text
        content=${props['content'] ?? ''}
        tone=${props['tone'] ?? 'analytical'}
      ></bi-narrative-text>
    `;
  }
  return nothing;
}
