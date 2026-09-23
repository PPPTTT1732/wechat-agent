import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, Tag, Github } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { SignedIn, SignedOut, SignInButton, UserButton, useUser } from '@clerk/clerk-react';

const API_URL = "https://wechat-agent-5y0i.onrender.com/api/v1/memory";
const PROJECT_ID = "mp-afritrips-v1"; // Plus tard, ce sera géré dynamiquement par l'organisation

function DashboardContent() {
  const { user } = useUser();
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchChunks = async () => {
    try {
      const res = await fetch(`${API_URL}/dashboard/chunks?project_id=${PROJECT_ID}`);
      if (!res.ok) throw new Error("Erreur serveur");
      const data = await res.json();
      setChunks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChunks();
  }, []);

  if (loading) return <div className="min-h-screen bg-gray-900 flex items-center justify-center">Chargement du cerveau d'équipe...</div>;

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-10 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
              AgentOps Dashboard
            </h1>
            <p className="text-gray-400 mt-2">Gestion du Cerveau d'Équipe pour {PROJECT_ID}</p>
          </div>
          <div className="flex gap-6 items-center">
            <div className="flex gap-4">
              <div className="bg-gray-800 px-4 py-2 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-400">{chunks.filter(c => c.status === 'TRUSTED').length}</div>
                <div className="text-xs text-gray-500 uppercase">Validés</div>
              </div>
              <div className="bg-gray-800 px-4 py-2 rounded-lg text-center">
                <div className="text-2xl font-bold text-yellow-400">{chunks.filter(c => c.status === 'PROPOSED').length}</div>
                <div className="text-xs text-gray-500 uppercase">En Attente</div>
              </div>
            </div>
            {/* Composant de profil utilisateur Clerk (Avatar) */}
            <div className="ml-4 border-l border-gray-700 pl-6 flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm font-bold text-white">{user?.fullName || "Lead Dev"}</div>
                <div className="text-xs text-gray-400">Admin</div>
              </div>
              <UserButton appearance={{ elements: { userButtonAvatarBox: "w-10 h-10" } }} />
            </div>
          </div>
        </header>

        {/* Le reste du contenu existant (Liste des Chunks) */}
        <div className="grid gap-6">
          {chunks.map(chunk => (
            <div key={chunk.id} className="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow-lg">
              <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-gray-300 whitespace-pre-wrap border border-gray-800">
                {chunk.content}
              </div>
            </div>
          ))}
          {chunks.length === 0 && <div className="text-center py-20 text-gray-500">Le cerveau est vide.</div>}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <>
      <SignedOut>
        {/* Page affichée si l'utilisateur n'est pas connecté */}
        <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center text-white">
          <div className="bg-gray-800 p-10 rounded-2xl shadow-2xl max-w-md w-full text-center border border-gray-700">
            <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
              AgentOps
            </h1>
            <p className="text-gray-400 mb-8">Plateforme SaaS pour développeurs WeChat</p>
            
            <SignInButton mode="modal">
              <button className="w-full flex items-center justify-center gap-3 bg-white text-gray-900 py-3 px-4 rounded-lg font-bold hover:bg-gray-100 transition-colors">
                <Github size={20} />
                Continuer avec GitHub
              </button>
            </SignInButton>
          </div>
        </div>
      </SignedOut>
      
      <SignedIn>
        {/* Page affichée si connecté avec succès */}
        <DashboardContent />
      </SignedIn>
    </>
  );
}
