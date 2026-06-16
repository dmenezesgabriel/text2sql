import { createComponent } from '@lit/react';
import React from 'react';

import { BiButton } from './bi-button';

export const BiButtonReact = createComponent({
  tagName: 'bi-button',
  elementClass: BiButton,
  react: React,
  events: {},
});
