import React from 'react';
import { useParams } from 'react-router-dom';

import { Card } from '@/shared/components/Card';

/**
 *
 */
export function QuestionDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h2>Question Detail</h2>
      <Card title={`Question ${id}`}>
        <p>Question details and visualization will render here.</p>
      </Card>
    </div>
  );
}
