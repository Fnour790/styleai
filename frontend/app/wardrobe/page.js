'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function WardrobePage() {
  const router = useRouter();
  const [items, setItems] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  // Charger les vêtements au démarrage
  useEffect(() => {
    fetchWardrobe();
  }, []);

  const fetchWardrobe = async () => {
    try {
      const res = await fetch('http://localhost:8000/wardrobe');
      const data = await res.json();
      setItems(data);
    } catch (error) {
      console.error('Erreur chargement garde-robe');
    }
  };

  const uploadPhoto = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/wardrobe/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setMessage(`✅ Vêtement ajouté avec succès !`);
      fetchWardrobe();
    } catch (error) {
      setMessage('❌ Erreur lors de l\'upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">

      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-zinc-800">
        <button onClick={() => router.push('/')} className="text-zinc-400 hover:text-white">
          ← Retour
        </button>
        <h1 className="font-semibold text-lg">
          Ma Garde-<span className="text-purple-500">robe</span>
        </h1>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-8">

        {/* Upload zone */}
        <label className="block w-full border-2 border-dashed border-zinc-700 hover:border-purple-500 rounded-2xl p-10 text-center cursor-pointer transition-colors mb-6">
          <input
            type="file"
            accept="image/*"
            onChange={uploadPhoto}
            className="hidden"
          />
          {uploading ? (
            <div>
              <div className="text-4xl mb-3">⏳</div>
              <p className="text-zinc-400">Analyse en cours par l'IA...</p>
            </div>
          ) : (
            <div>
              <div className="text-4xl mb-3">📸</div>
              <p className="text-white font-semibold">Clique pour uploader un vêtement</p>
              <p className="text-zinc-500 text-sm mt-1">JPG, PNG ou WebP</p>
            </div>
          )}
        </label>

        {/* Message de confirmation */}
        {message && (
          <div className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 mb-6 text-sm">
            {message}
          </div>
        )}

        {/* Liste des vêtements */}
        {items.length === 0 ? (
          <div className="text-center text-zinc-500 py-20">
            <div className="text-5xl mb-4">👗</div>
            <p>Ta garde-robe est vide</p>
            <p className="text-sm mt-1">Upload ta première photo !</p>
          </div>
        ) : (
          <div>
            <h2 className="text-zinc-400 text-sm mb-4">{items.length} vêtement(s)</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {items.map((item) => (
                <div key={item.id} className="bg-zinc-900 rounded-2xl overflow-hidden border border-zinc-800">
                  <img
                    src={`http://localhost:8000${item.image_url}`}
                    alt={item.category}
                    className="w-full h-40 object-cover"
                  />
                  <div className="p-3">
                    <p className="font-semibold text-sm capitalize">{item.category}</p>
                    <p className="text-zinc-500 text-xs mt-1">
                      {item.style_tags?.slice(0, 2).join(', ')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}