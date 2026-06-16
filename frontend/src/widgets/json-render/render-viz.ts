import './components/bar-chart/bar-chart';
import './components/data-table/data-table';
import './components/line-chart/line-chart';
import './components/metric/metric';
import './components/narrative-text/narrative-text';
import './components/pie-chart/pie-chart';

import { html, nothing, type TemplateResult } from 'lit';

type VizTemplate = TemplateResult<1> | typeof nothing;
type VizProps = Record<string, unknown>;

/**
 *
 * @param props
 */
function renderBarChart(props: VizProps): VizTemplate {
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

/**
 *
 * @param props
 */
function renderLineChart(props: VizProps): VizTemplate {
  return html`
    <bi-line-chart
      title=${props['title'] ?? ''}
      .xAxis=${props['xAxis'] ?? ''}
      .yAxis=${props['yAxis'] ?? ''}
      .data=${props['data'] ?? []}
    ></bi-line-chart>
  `;
}

/**
 *
 * @param props
 */
function renderPieChart(props: VizProps): VizTemplate {
  return html`
    <bi-pie-chart title=${props['title'] ?? ''} .data=${props['data'] ?? []}></bi-pie-chart>
  `;
}

/**
 *
 * @param props
 */
function renderDataTable(props: VizProps): VizTemplate {
  return html`
    <bi-data-table
      title=${props['title'] ?? ''}
      .columns=${props['columns'] ?? []}
      .rows=${props['rows'] ?? []}
    ></bi-data-table>
  `;
}

/**
 *
 * @param props
 */
function renderMetric(props: VizProps): VizTemplate {
  return html`
    <bi-metric
      label=${props['label'] ?? ''}
      value=${props['value'] ?? ''}
      change=${props['change'] ?? ''}
      direction=${props['direction'] ?? 'neutral'}
    ></bi-metric>
  `;
}

/**
 *
 * @param props
 */
function renderNarrativeText(props: VizProps): VizTemplate {
  return html`
    <bi-narrative-text
      content=${props['content'] ?? ''}
      tone=${props['tone'] ?? 'analytical'}
    ></bi-narrative-text>
  `;
}

const renderersByComponent: Partial<Record<string, (props: VizProps) => VizTemplate>> = {
  BarChart: renderBarChart,
  LineChart: renderLineChart,
  PieChart: renderPieChart,
  DataTable: renderDataTable,
  Metric: renderMetric,
  NarrativeText: renderNarrativeText,
};

/**
 * Renders a visualization component template.
 * @param component - Component name (e.g., 'BarChart', 'DataTable')
 * @param props - Component props object
 * @returns Lit template or nothing if component not found
 */
export function renderViz(component: string, props: VizProps): VizTemplate {
  return renderersByComponent[component]?.(props) ?? nothing;
}
