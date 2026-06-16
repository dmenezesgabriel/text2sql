import { createComponent } from '@lit/react';
import React from 'react';

import { BiDashboardTile } from './bi-dashboard-tile';

export const BiDashboardTileReact = createComponent({
  tagName: 'bi-dashboard-tile',
  elementClass: BiDashboardTile,
  react: React,
  events: {},
});
