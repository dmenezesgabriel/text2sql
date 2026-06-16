import { createComponent } from '@lit/react';
import React from 'react';

import { BiInput } from './bi-input';

export const BiInputReact = createComponent({
  tagName: 'bi-input',
  elementClass: BiInput,
  react: React,
  events: {
    onBiInputChange: 'bi-input-change',
  },
});
