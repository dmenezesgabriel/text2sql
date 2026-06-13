import React, { useState } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
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
  fontSize: '14px',
  outline: 'none',
  fontFamily: 'inherit',
};

/**
 *
 * @param root0
 * @param root0.onSend
 * @param root0.disabled
 */
export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
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
        onChange={(e) => { setValue(e.target.value); }}
        placeholder="Ask a question about your data..."
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  );
}
