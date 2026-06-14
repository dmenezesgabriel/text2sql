import '@/features/chat/ui/chat-input/bi-chat-input';
import '@/features/chat/ui/chat-message/bi-chat-message';

import { css, html, LitElement } from 'lit';
import { state } from 'lit/decorators.js';

import type { AgentEvent, AgentMessage } from '@/entities/agent/types';
import { sendChatMessage } from '@/features/chat/api/chat-api';

export class BiChatPage extends LitElement {
  static readonly styles = css`
    :host {
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    .messages {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
      padding: var(--spacing-md) 0;
    }
    .empty {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--color-text-secondary);
      font-size: var(--text-sm);
    }
  `;

  @state() private _messages: AgentMessage[] = [];
  @state() private _isStreaming = false;
  @state() private _conversationId: string | null = null;

  private _appendToLast(fragment: string) {
    const msgs = [...this._messages];
    const last = msgs.at(-1);
    if (last?.role === 'assistant') {
      msgs[msgs.length - 1] = { ...last, content: last.content + fragment };
    }
    this._messages = msgs;
  }

  private _setSpecOnLast(spec: Record<string, unknown>) {
    const msgs = [...this._messages];
    const last = msgs.at(-1);
    if (last?.role === 'assistant') {
      msgs[msgs.length - 1] = { ...last, spec };
    }
    this._messages = msgs;
  }

  private _handleEvent(event: AgentEvent) {
    if (event.type === 'ThinkingEvent') {
      this._appendToLast(event.payload as string);
    } else if (event.type === 'SpecFragmentEvent') {
      this._setSpecOnLast(event.payload as Record<string, unknown>);
    }
  }

  private readonly _handleSend = (e: CustomEvent<string>) => {
    const content = e.detail;
    if (!content || this._isStreaming) return;

    const convId = this._conversationId ?? crypto.randomUUID();
    if (!this._conversationId) this._conversationId = convId;

    this._messages = [
      ...this._messages,
      { id: crypto.randomUUID(), role: 'user', content, createdAt: new Date().toISOString() },
      {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        createdAt: new Date().toISOString(),
      },
    ];
    this._isStreaming = true;

    sendChatMessage(
      content,
      convId,
      (event) => {
        this._handleEvent(event);
      },
      () => {
        this._isStreaming = false;
      },
      () => {
        this._isStreaming = false;
      },
    );
  };

  render() {
    return html`
      ${this._messages.length === 0
        ? html`<div class="empty">Ask a question about your data to get started.</div>`
        : html`
            <div class="messages">
              ${this._messages.map(
                (msg) => html`<bi-chat-message .message=${msg}></bi-chat-message>`,
              )}
            </div>
          `}
      <bi-chat-input ?disabled=${this._isStreaming} @send=${this._handleSend}></bi-chat-input>
    `;
  }
}

customElements.define('bi-chat-page', BiChatPage);
