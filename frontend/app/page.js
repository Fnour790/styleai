'use client';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center px-6">
      
      {/* Logo */}
      <div className="mb-8 text-center">
        <h1 className="text-6xl font-bold tracking-tight">
          Style<span className="text-purple-500">AI</span>
        </h1>
        <p className="text-zinc-400 mt-3 text-lg">
          Ton styliste personnel propulsé par l'IA
        </p>
      </div>

      {/* Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl mb-10">
        
        <div className="bg-zinc-900 rounded-2xl p-6 text-center border border-zinc-800">
          <div className="text-4xl mb-3">👗</div>
          <h2 className="font-semibold text-white">Garde-robe</h2>
          <p className="text-zinc-500 text-sm mt-1">Upload tes vêtements</p>
        </div>

        <div className="bg-zinc-900 rounded-2xl p-6 text-center border border-zinc-800">
          <div className="text-4xl mb-3">🌤️</div>
          <h2 className="font-semibold text-white">Météo</h2>
          <p className="text-zinc-500 text-sm mt-1">Tenues adaptées au temps</p>
        </div>

        <div className="bg-zinc-900 rounded-2xl p-6 text-center border border-zinc-800">
          <div className="text-4xl mb-3">🤖</div>
          <h2 className="font-semibold text-white">Chat AI</h2>
          <p className="text-zinc-500 text-sm mt-1">Conseils personnalisés</p>
        </div>

      </div>

      {/* Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 w-full max-w-sm">
        <button
          onClick={() => router.push('/chat')}
          className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-full transition-colors"
        >
          Chat avec le styliste
        </button>
        <button
          onClick={() => router.push('/wardrobe')}
          className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold py-3 rounded-full transition-colors"
        >
          Ma garde-robe
        </button>
      </div>

    </div>
  );
}