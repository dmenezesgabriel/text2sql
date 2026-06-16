import type React from 'react';

// React.DetailedHTMLProps = ClassAttributes<T> & HTMLAttributes<T>, which adds key/ref
type LitProps<T = object> = React.DetailedHTMLProps<
  React.HTMLAttributes<HTMLElement>,
  HTMLElement
> &
  T;

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'bi-badge': LitProps<{
        variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'mono';
      }>;
      'bi-spinner': LitProps<{
        size?: 'sm' | 'md' | 'lg';
      }>;
      'bi-card': LitProps<{
        heading?: string;
        padding?: 'sm' | 'md' | 'lg';
      }>;
      'bi-empty-state': LitProps<{
        heading?: string;
        description?: string;
      }>;
      'bi-page-header': LitProps<{
        heading?: string;
        description?: string;
      }>;
      'bi-input': LitProps<{
        label?: string;
        value?: string;
        placeholder?: string;
        disabled?: boolean;
        error?: string;
        hint?: string;
        type?: 'text' | 'email' | 'search' | 'url';
        required?: boolean;
      }>;
      'bi-button': LitProps<{
        variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
        size?: 'sm' | 'md';
        disabled?: boolean;
        type?: 'button' | 'submit' | 'reset';
      }>;
      'bi-question-card': LitProps<{
        'question-id'?: string;
        title?: string;
        'viz-format'?: string;
        sql?: string;
        'created-at'?: string;
        'show-delete'?: boolean | string;
      }>;
      'bi-dashboard-tile': LitProps<{
        'tile-id'?: string;
        heading?: string;
        col?: number;
        width?: number;
        row?: number;
        height?: number;
        filtered?: boolean | string;
      }>;
      'bi-dashboard-grid': LitProps<{
        heading?: string;
      }>;
      'bi-header': LitProps;
    }
  }
}
