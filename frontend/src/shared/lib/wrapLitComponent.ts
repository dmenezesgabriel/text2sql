import { createComponent } from '@lit/react';
import * as React from 'react';

/**
 *
 * @param tagName
 * @param elementClass
 */
export function wrapLitComponent(
  tagName: string,
  elementClass: CustomElementConstructor,
): React.ComponentType<Record<string, unknown>> {
  return createComponent({
    tagName,
    elementClass,
    react: React,
    events: {},
  });
}
