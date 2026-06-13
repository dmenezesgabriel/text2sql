import React from 'react';
import { BrowserRouter } from 'react-router-dom';

import { JsonRenderProvider } from '@/widgets/json-render/json-render-provider';

interface ProvidersProps {
  readonly children: React.ReactNode;
}

/**
 *
 * @param root0
 * @param root0.children
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <BrowserRouter>
      <JsonRenderProvider>{children}</JsonRenderProvider>
    </BrowserRouter>
  );
}
