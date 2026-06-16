import { createComponent } from '@lit/react';
import React from 'react';

import { BiDashboardGrid } from './bi-dashboard-grid';

export const BiDashboardGridReact = createComponent({
  tagName: 'bi-dashboard-grid',
  elementClass: BiDashboardGrid,
  react: React,
  events: {},
});
