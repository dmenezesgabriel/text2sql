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
export function DatasetsPage() {
  return (
    <div style={pageStyle}>
      <h2>Datasets</h2>
      <Card title="Register a Dataset">
        <p>Connect tables, files from S3, or external databases.</p>
      </Card>
    </div>
  );
}
