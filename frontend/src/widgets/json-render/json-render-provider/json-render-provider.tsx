import React from 'react';

interface JsonRenderProviderProps {
  children: React.ReactNode;
}

/**
 *
 * @param root0
 * @param root0.children
 */
export function JsonRenderProvider({ children }: JsonRenderProviderProps) {
  return React.createElement(React.Fragment, null, children);
}
