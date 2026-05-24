'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Salut ! Je suis ton styliste personnel AI 👗 Dis-moi ce que tu cherches aujourd\'hui !'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          history: messages.filter(m => m.role !== 'assistant' || messages.indexOf(m) > 0),
        }),
      });

      const data = await response.json();
      setMessages([...newMessages, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: 'Désolé, je ne peux pas me connecter au serveur. Vérifie que le backend tourne !' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-zinc-800">
        <button onClick={() => router.push('/')} className="text-zinc-400 hover:text-white">
          ← Retour
        </button>
        <h1 className="font-semibold text-lg">
          Style<span className="text-purple-500">AI</span> Chat
        </h1>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 max-w-2xl w-full mx-auto">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs sm:max-w-md px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-purple-600 text-white'
                : 'bg-zinc-900 text-zinc-100 border border-zinc-800'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-zinc-900 border border-zinc-800 px-4 py-3 rounded-2xl text-zinc-400 text-sm">
              En train de réfléchir...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="px-4 py-4 border-t border-zinc-800">
        <div className="flex gap-3 max-w-2xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Demande un conseil style..."
            className="flex-1 bg-zinc-900 border border-zinc-700 rounded-full px-5 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-purple-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-semibold px-6 py-3 rounded-full transition-colors"
          >
            Envoyer
          </button>
        </div>
      </div>

    </div>
  );
}
