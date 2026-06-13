import { useParams } from 'react-router-dom';

import { Card } from '@/shared/components/card';

/**
 *
 */
export function DatasetDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h2>Dataset</h2>
      <Card title={`Dataset ${String(id)}`}>
        <p>Schema browser and data preview will render here.</p>
      </Card>
    </div>
  );
}
