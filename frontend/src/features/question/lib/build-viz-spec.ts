import type { Spec } from '@json-render/react';

import type { Question } from '@/entities/question/types';

type VizFields = Pick<Question, 'vizComponent' | 'vizProps' | 'vizChildren'>;

/**
 * Builds a single-element json-render spec for a saved question's visualization.
 * @param q - Subset of Question fields describing the viz
 * @param q.vizComponent
 * @param q.vizProps
 * @param q.vizChildren
 * @example
 * buildVizSpec({ vizComponent: 'BarChart', vizProps: { title: 'Revenue', ... }, vizChildren: [] })
 */
export function buildVizSpec({ vizComponent, vizProps, vizChildren }: VizFields): Spec {
  return {
    root: 'main',
    elements: {
      main: {
        type: vizComponent,
        props: vizProps,
        children: (vizChildren as string[] | undefined) ?? [],
      },
    },
  };
}
