import { useParams } from 'react-router-dom';

import { Card } from '@/shared/components/card';

/**
 *
 */
export function DashboardDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h2>Dashboard</h2>
      <Card title={`Dashboard ${String(id)}`}>
        <p>Dashboard grid with tiles will render here.</p>
      </Card>
    </div>
  );
}
