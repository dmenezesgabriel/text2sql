import './styles/global.css';
// Register Lit elements
import '@/widgets/json-render/components/bar-chart';
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
