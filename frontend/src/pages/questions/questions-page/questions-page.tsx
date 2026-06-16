import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { useQuestionStore } from '@/features/question/model/store';
import { BiQuestionCardReact } from '@/features/question/ui/question-card';

/**
 *
 */
export function QuestionsPage() {
  const { questions, isLoading, error, fetchQuestions, deleteQuestion } = useQuestionStore();
  const navigate = useNavigate();

  useEffect(() => {
    void fetchQuestions();
  }, [fetchQuestions]);

  const handleDelete = (e: Event) => {
    void deleteQuestion((e as CustomEvent<string>).detail);
  };

  return (
    <div className="flex flex-col gap-lg">
      <bi-page-header
        heading="Questions"
        description="Saved analytical queries and their visualizations"
      >
        <bi-button
          slot="actions"
          variant="primary"
          onClick={() => {
            void navigate('/chat');
          }}
        >
          Go to Chat
        </bi-button>
      </bi-page-header>

      {isLoading && questions.length === 0 && <bi-spinner />}

      {error && (
        <p role="alert" aria-live="assertive" className="text-error text-sm">
          {error}
        </p>
      )}

      {!isLoading && !error && questions.length === 0 && (
        <bi-empty-state
          heading="No questions yet"
          description="Ask a question in the chat, then save it here."
        >
          <bi-button
            slot="action"
            variant="primary"
            onClick={() => {
              void navigate('/chat');
            }}
          >
            Go to Chat
          </bi-button>
        </bi-empty-state>
      )}

      {questions.length > 0 && (
        <div className="grid-auto-fill-lg">
          {questions.map((q) => (
            <BiQuestionCardReact
              key={q.id}
              questionId={q.id}
              title={q.title}
              vizFormat={q.vizFormat}
              sql={q.sql}
              createdAt={q.createdAt}
              showDelete={true}
              onBiQuestionDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
