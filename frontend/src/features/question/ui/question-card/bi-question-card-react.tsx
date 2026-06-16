import { createComponent } from '@lit/react';
import React from 'react';

import { BiQuestionCard } from './bi-question-card';

export const BiQuestionCardReact = createComponent({
  tagName: 'bi-question-card',
  elementClass: BiQuestionCard,
  react: React,
  events: {
    onBiQuestionDelete: 'bi-question-delete',
  },
});
