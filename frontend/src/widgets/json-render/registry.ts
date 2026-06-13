import { defineRegistry } from '@json-render/react';

import { wrapLitComponent } from '@/shared/lib/wrap-lit-component';

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

export { biCatalog } from './catalog';
