import React from 'react';

import { useChatStore } from '@/features/chat/model/store';
import { Card } from '@/shared/components/Card';
import { Spinner } from '@/shared/components/Spinner';

const pageStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--spacing-lg)',
};

const gridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
  gap: 'var(--spacing-md)',
};

/**
 *
 */
export function QuestionsPage() {
  const messages = useChatStore((s) => s.messages);

  const savedQuestions = messages
    .filter((m) => m.role === 'assistant' && m.content.length > 0)
    .slice(-6);

  return (
    <div style={pageStyle}>
      <h2>Questions</h2>
      {savedQuestions.length === 0 ? (
        <Card title="No saved questions yet">
          <p>Ask a question in the chat to get started.</p>
        </Card>
      ) : (
        <div style={gridStyle}>
          {savedQuestions.map((q) => (
            <Card key={q.id} title="Saved Response">
              <p>{q.content.slice(0, 120)}...</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
