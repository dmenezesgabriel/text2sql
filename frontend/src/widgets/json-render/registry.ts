import { type Components, defineRegistry } from '@json-render/react';
import React from 'react';

import { wrapLitComponent } from '@/shared/lib/wrap-lit-component';

import { biCatalog } from './catalog';
import { BarChartElement } from './components/bar-chart/bar-chart';
import { DataTableElement } from './components/data-table/data-table';
import { MetricElement } from './components/metric/metric';
import { NarrativeTextElement } from './components/narrative-text/narrative-text';

// @json-render/react ComponentFn receives { props, ... } (a ComponentContext),
// not the raw props object. We wrap each Lit component so it extracts props
// from the context before forwarding them to the Lit React element.
/**
 *
 * @param tagName
 * @param elementClass
 */
function asComponentFn(tagName: string, elementClass: CustomElementConstructor) {
  const LitComponent = wrapLitComponent(tagName, elementClass);
  return ({ props }: { props: Record<string, unknown> }) =>
    React.createElement(LitComponent, props);
}

const components = {
  BarChart: asComponentFn('bi-bar-chart', BarChartElement),
  DataTable: asComponentFn('bi-data-table', DataTableElement),
  Metric: asComponentFn('bi-metric', MetricElement),
  NarrativeText: asComponentFn('bi-narrative-text', NarrativeTextElement),
} as unknown as Components<typeof biCatalog>;

const { registry } = defineRegistry(biCatalog, {
  components,
  actions: {
    save_as_question: async () => {},
    add_to_dashboard: async () => {},
    export_data: async () => {},
    drill_down: async () => {},
  },
});

export { registry };

export { biCatalog } from './catalog';
