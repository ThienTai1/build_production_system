'use server';

import { createUIMessageStream, createUIMessageStreamResponse, generateId } from 'ai';

export async function chat({ messages }: { messages: any[] }) {
  const lastMessage = messages[messages.length - 1];

  // Support both older 'content' and newer 'parts' structure for safety
  const question = typeof lastMessage.content === 'string'
    ? lastMessage.content
    : (lastMessage.parts?.filter((p: any) => p.type === 'text').map((p: any) => p.text).join('\n') || '');

  const stream = createUIMessageStream({
    execute: async ({ writer }) => {
      const id = generateId(); // AI SDK v6 requires consistent ID for message chunks
      try {
        // Call FastAPI Backend (Port 8003)
        const response = await fetch(`http://127.0.0.1:8003/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question }),
        });

        if (!response.ok) throw new Error('Backend failed');

        const data = await response.json();

        // Start text part
        writer.write({ type: 'text-start', id });

        // Write text response
        writer.write({ type: 'text-delta', delta: data.answer, id });

        // End text part
        writer.write({ type: 'text-end', id });

        // Write metadata as data annotations
        writer.write({
          type: 'data-latency',
          data: data.latency,
          id
        });
        writer.write({
          type: 'data-sources',
          data: data.sources,
          id
        });
      } catch (error) {
        writer.write({ type: 'error', errorText: (error as Error).message });
      }
    },
  });

  return stream;
}
