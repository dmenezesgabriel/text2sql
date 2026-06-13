import React from 'react';

import { Card } from '@/shared/components/card';

const pageStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--spacing-lg)',
};

/**
 *
 */
export function DashboardsPage() {
  return (
    <div style={pageStyle}>
      <h2>Dashboards</h2>
      <Card title="Getting Started">
        <p>Compose multiple questions into interactive dashboards with cross-filtering.</p>
      </Card>
    </div>
  );
}
