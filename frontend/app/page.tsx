'use client';

import { useChat } from '@ai-sdk/react';
import { useState } from 'react';
import { Bot, User, Send, Loader2 } from 'lucide-react';
import { chat } from './actions';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const { messages, sendMessage, status } = useChat({
    transport: {
      sendMessages: chat,
      reconnectToStream: async () => null,
    }
  });

  const isPending = status === 'submitted' || status === 'streaming';

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (input.trim()) {
      sendMessage({ text: input });
      setInput('');
    }
  };

  return (
    <main className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="p-4 bg-white border-b shadow-sm flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">AI Agent M4 (Gemma 2 + Milvus)</h1>
        <div className="text-xs text-green-500 font-medium px-2 py-1 bg-green-50 rounded-full border border-green-200">
          System Online
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center mt-20 text-gray-400">
            <Bot className="w-12 h-12 mx-auto mb-2 opacity-20" />
            <p>The RAG system is ready. Try asking about the system!</p>
          </div>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] flex gap-3 p-4 rounded-2xl ${m.role === 'user' ? 'bg-blue-600 text-white shadow-blue-200' : 'bg-white text-gray-800 shadow-sm border'
              } shadow-md`}>
              {m.role === 'assistant' && <Bot className="w-5 h-5 mt-1 text-blue-500" />}
              <div className="flex flex-col">
                {m.parts && m.parts.length > 0 ? (
                  m.parts.map((part: any, i: number) => (
                    part.type === 'text' ? (
                      <p key={i} className="leading-relaxed whitespace-pre-wrap">{part.text}</p>
                    ) : null
                  ))
                ) : (
                  <p className="leading-relaxed whitespace-pre-wrap">{m.content}</p>
                )}
              </div>
              {m.role === 'user' && <User className="w-5 h-5 mt-1 text-blue-100" />}
            </div>
          </div>
        ))}
        {isPending && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-500 p-3 rounded-2xl shadow-sm border flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
              <span className="text-sm italic">Agent is thinking...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t shadow-lg">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
          <input
            type="text"
            className="w-full p-4 pr-12 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-inner text-gray-700"
            placeholder="Type your message here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isPending}
          />
          <button
            type="submit"
            disabled={isPending || !input.trim()}
            className="absolute right-3 top-3 p-2 bg-blue-600 text-white rounded-lg disabled:bg-gray-300 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </main>
  );
}