import React, { useState } from 'react';

interface ChatInputProps {
  readonly onSend: (message: string) => void;
  readonly disabled: boolean;
}

const formStyle: React.CSSProperties = {
  display: 'flex',
  gap: 'var(--spacing-sm)',
  padding: 'var(--spacing-md)',
  borderTop: '1px solid var(--color-border)',
  background: 'var(--color-bg)',
};

const inputStyle: React.CSSProperties = {
  flex: 1,
  padding: 'var(--spacing-sm) var(--spacing-md)',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--color-border)',
  background: 'var(--color-surface)',
  color: 'var(--color-text)',
  fontSize: 'var(--text-base)',
  outline: 'none',
  fontFamily: 'inherit',
};

const sendButtonStyle: React.CSSProperties = {
  padding: 'var(--spacing-sm) var(--spacing-md)',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: 'var(--color-primary)',
  color: '#ffffff',
  fontSize: 'var(--text-base)',
  fontWeight: 500,
  fontFamily: 'inherit',
  cursor: 'pointer',
};

/**
 *
 * @param root0
 * @param root0.onSend
 * @param root0.disabled
 */
export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: React.SyntheticEvent) => {
    e.preventDefault();
    if (value.trim() && !disabled) {
      onSend(value.trim());
      setValue('');
    }
  };

  return (
    <form style={formStyle} onSubmit={handleSubmit}>
      <input
        style={inputStyle}
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
        }}
        placeholder="Ask a question about your data..."
        disabled={disabled}
      />
      <button type="submit" style={sendButtonStyle} disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  );
}
