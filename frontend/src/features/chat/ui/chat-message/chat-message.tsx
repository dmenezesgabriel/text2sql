import type { Spec } from '@json-render/react';
import { JSONUIProvider, Renderer } from '@json-render/react';
import { useState } from 'react';

import type { AgentMessage } from '@/entities/agent/types';
import { specToQuestionPayload } from '@/features/question/lib/spec-to-question-payload';
import { useQuestionStore } from '@/features/question/model/store';
import { registry } from '@/widgets/json-render/registry';

interface ChatMessageProps {
  readonly message: AgentMessage;
}

/**
 *
 * @param isUser
 * @param hasError
 */
function parseTextColor(isUser: boolean, hasError: boolean): string {
  if (isUser) return '#ffffff';
  if (hasError) return 'var(--color-error, #d32f2f)';
  return 'var(--color-text)';
}

/**
 *
 * @param saved
 * @param isSaving
 */
function parseSaveButtonLabel(saved: boolean, isSaving: boolean): string {
  if (saved) return 'Saved!';
  if (isSaving) return 'Saving…';
  return 'Save as Question';
}

/**
 *
 * @param root0
 * @param root0.message
 */
export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [saved, setSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const textColor = parseTextColor(isUser, Boolean(message.error));
  const saveButtonLabel = parseSaveButtonLabel(saved, isSaving);

  const handleSaveAsQuestion = async () => {
    if (!message.spec) return;
    setIsSaving(true);
    try {
      await useQuestionStore.getState().createQuestion(specToQuestionPayload(message.spec));
      setSaved(true);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
        gap: 'var(--spacing-xs)',
      }}
    >
      <div
        style={{
          maxWidth: isUser ? '70%' : '100%',
          width: !isUser && message.spec ? '100%' : undefined,
          padding: isUser ? 'var(--spacing-sm) var(--spacing-md)' : 0,
          borderRadius: 'var(--radius-md)',
          background: isUser ? 'var(--color-primary)' : 'transparent',
          color: textColor,
          fontSize: 'var(--text-base)',
          lineHeight: 'var(--leading-normal)',
        }}
      >
        {!isUser && message.spec ? (
          <JSONUIProvider registry={registry}>
            <Renderer spec={message.spec as Spec} registry={registry} />
          </JSONUIProvider>
        ) : (
          message.content
        )}
      </div>

      {!isUser && message.spec && (
        <div className="flex items-center gap-sm">
          <bi-button
            variant="ghost"
            size="sm"
            disabled={isSaving || saved}
            onClick={() => void handleSaveAsQuestion()}
          >
            {saveButtonLabel}
          </bi-button>
          {saved && (
            <p role="status" className="text-xs text-secondary">
              Question saved
            </p>
          )}
        </div>
      )}
    </div>
  );
}
