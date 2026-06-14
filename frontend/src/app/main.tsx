import './styles/global.css';
// Register shared Lit elements
import '@/shared/components/badge/bi-badge';
import '@/shared/components/button/bi-button';
import '@/shared/components/card/bi-card';
import '@/shared/components/empty-state/bi-empty-state';
import '@/shared/components/header/bi-header';
import '@/shared/components/input/bi-input';
import '@/shared/components/page-header/bi-page-header';
import '@/shared/components/spinner/bi-spinner';
// Register feature Lit elements
import '@/features/question/ui/question-card/bi-question-card';
import '@/features/dashboard/ui/dashboard-tile/bi-dashboard-tile';
import '@/features/dashboard/ui/dashboard-grid/bi-dashboard-grid';
// Register visualization Lit elements
import '@/widgets/json-render/components/bar-chart';
import '@/widgets/json-render/components/line-chart';
import '@/widgets/json-render/components/pie-chart';
import '@/widgets/json-render/components/data-table';
import '@/widgets/json-render/components/metric';
import '@/widgets/json-render/components/narrative-text';

import React from 'react';
import ReactDOM from 'react-dom/client';

import { App } from './app';
import { Providers } from './providers';

ReactDOM.createRoot(document.querySelector('#root')!).render(
  <React.StrictMode>
    <Providers>
      <App />
    </Providers>
  </React.StrictMode>,
);
