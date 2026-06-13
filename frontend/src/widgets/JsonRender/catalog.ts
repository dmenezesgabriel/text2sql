import { defineCatalog } from '@json-render/core';
import { schema } from '@json-render/react/schema';
import { z } from 'zod';

export const biCatalog = defineCatalog(schema, {
  components: {
    BarChart: {
      props: z.object({
        title: z.string(),
        xAxis: z.string(),
        yAxis: z.string(),
        data: z.array(z.object({ label: z.string(), value: z.number() })),
        color: z.string().optional(),
      }),
      description: 'Vertical bar chart for comparing values across categories',
    },
    LineChart: {
      props: z.object({
        title: z.string(),
        xAxis: z.string(),
        yAxis: z.string(),
        data: z.array(z.object({ label: z.string(), value: z.number() })),
        color: z.string().optional(),
      }),
      description: 'Line chart for trends over time',
    },
    PieChart: {
      props: z.object({
        title: z.string(),
        data: z.array(z.object({ label: z.string(), value: z.number() })),
      }),
      description: 'Pie chart for proportion breakdown',
    },
    DataTable: {
      props: z.object({
        title: z.string().optional(),
        columns: z.array(
          z.object({
            key: z.string(),
            header: z.string(),
            format: z.string().optional(),
          }),
        ),
        rows: z.array(z.record(z.any())),
      }),
      description: 'Tabular data display with sortable columns',
    },
    Metric: {
      props: z.object({
        label: z.string(),
        value: z.string(),
        change: z.string().optional(),
        direction: z.enum(['up', 'down', 'neutral']).optional(),
      }),
      description: 'Single KPI metric with optional trend indicator',
    },
    NarrativeText: {
      props: z.object({
        content: z.string(),
        tone: z.enum(['analytical', 'conversational', 'executive']).optional(),
      }),
      description: 'Data-driven narrative text response',
    },
  },
  actions: {
    save_as_question: {
      description: 'Save response as a question artifact',
    },
    add_to_dashboard: {
      description: 'Add this viz to a dashboard',
    },
    export_data: {
      description: 'Export underlying data as CSV',
    },
    drill_down: {
      description: 'Filter by a dimension value',
    },
  },
});
