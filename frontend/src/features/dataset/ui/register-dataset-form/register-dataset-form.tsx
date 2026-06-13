import React, { useState } from 'react';

import { useDatasetStore } from '../../model/store';

const formStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--spacing-sm)',
};

const inputStyle: React.CSSProperties = {
  padding: 'var(--spacing-sm) var(--spacing-md)',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--color-border)',
  fontSize: '0.9rem',
  background: 'var(--color-bg-primary)',
  color: 'var(--color-text-primary)',
};

const buttonStyle: React.CSSProperties = {
  padding: 'var(--spacing-sm) var(--spacing-md)',
  borderRadius: 'var(--radius-sm)',
  border: 'none',
  background: 'var(--color-primary)',
  color: '#ffffff',
  cursor: 'pointer',
  fontWeight: 600,
};

/**
 *
 */
export function RegisterDatasetForm() {
  const [name, setName] = useState('');
  const [s3Uri, setS3Uri] = useState('');
  const { registerDataset, isLoading, error } = useDatasetStore();

  const handleSubmit = (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!name.trim() || !s3Uri.trim()) return;
    void registerDataset(name.trim(), s3Uri.trim()).then(() => {
      setName('');
      setS3Uri('');
    });
  };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <input
        placeholder="Dataset name"
        value={name}
        onChange={(e) => {
          setName(e.target.value);
        }}
        style={inputStyle}
        disabled={isLoading}
      />
      <input
        placeholder="S3 URI (e.g. s3://bi-data/sales.parquet)"
        value={s3Uri}
        onChange={(e) => {
          setS3Uri(e.target.value);
        }}
        style={inputStyle}
        disabled={isLoading}
      />
      <button
        type="submit"
        disabled={isLoading || !name.trim() || !s3Uri.trim()}
        style={buttonStyle}
      >
        {isLoading ? 'Registering...' : 'Register Dataset'}
      </button>
      {error && <p style={{ color: 'red', fontSize: '0.85rem', margin: 0 }}>{error}</p>}
    </form>
  );
}
