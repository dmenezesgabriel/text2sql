import React from 'react';
import { useParams } from 'react-router-dom';

import { Card } from '@/shared/components/Card';

/**
 *
 */
export function DatasetDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h2>Dataset</h2>
      <Card title={`Dataset ${id}`}>
        <p>Schema browser and data preview will render here.</p>
      </Card>
    </div>
  );
}
