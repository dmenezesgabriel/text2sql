import React from 'react';
import { useParams } from 'react-router-dom';

import { Card } from '@/shared/components/Card';

/**
 *
 */
export function DashboardDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h2>Dashboard</h2>
      <Card title={`Dashboard ${id}`}>
        <p>Dashboard grid with tiles will render here.</p>
      </Card>
    </div>
  );
}
