import { defineRegistry } from '@json-render/react';
import React from 'react';

import { wrapLitComponent } from '@/shared/lib/wrapLitComponent';

import { biCatalog } from './catalog';

const { registry } = defineRegistry(biCatalog, {
  components: {
    BarChart: wrapLitComponent('bi-bar-chart', customElements.get('bi-bar-chart')!),
    DataTable: wrapLitComponent('bi-data-table', customElements.get('bi-data-table')!),
    Metric: wrapLitComponent('bi-metric', customElements.get('bi-metric')!),
    NarrativeText: wrapLitComponent('bi-narrative-text', customElements.get('bi-narrative-text')!),
  },
});

export { registry };

interface JsonRenderProviderProps {
  children: React.ReactNode;
}

/**
 *
 * @param root0
 * @param root0.children
 */
export function JsonRenderProvider({ children }: JsonRenderProviderProps) {
  return React.createElement(React.Fragment, null, children);
}

export {biCatalog} from './catalog';