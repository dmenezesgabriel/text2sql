import './styles/global.css';
// Register Lit elements
import '@/widgets/JsonRender/components/BarChart';
import '@/widgets/JsonRender/components/DataTable';
import '@/widgets/JsonRender/components/Metric';
import '@/widgets/JsonRender/components/NarrativeText';

import React from 'react';
import ReactDOM from 'react-dom/client';

import { App } from './App';
import { Providers } from './providers';

ReactDOM.createRoot(document.querySelector('#root')!).render(
  <React.StrictMode>
    <Providers>
      <App />
    </Providers>
  </React.StrictMode>,
);
