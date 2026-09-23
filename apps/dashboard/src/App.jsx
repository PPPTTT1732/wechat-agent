import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, Tag, Github } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { SignedIn, SignedOut, SignInButton, UserButton, useUser } from '@clerk/clerk-react';

const API_URL = "https://wechat-agent-5y0i.onrender.com/api/v1/memory";
const PROJECT_ID = "mp-afritrips-v1";

function DashboardContent() {
  const { user } = useUser();
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchChunks = async () => {
    try {
      const res = await fetch(`${API_URL}/dashboard/chunks?project_id=${PROJECT_ID}`);
      const data = await res.json();
      setChunks(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChunks();
  }, []);

  const updateStatus = async (id, newStatus) => {
    try {
      await fetch(`${API_URL}/dashboard/chunks/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchChunks();
    } catch (err) {
      alert("Erreur lors de la mise à jour");
    }
  };

  const addTag = async (id, currentMetadata) => {
    const tag = prompt("Entrez un tag (ex: navigation, api, ui):");
    if (!tag) return;
    
    const tags = currentMetadata?.tags || [];
    if (!tags.includes(tag)) {
      try {
        await fetch(`${API_URL}/dashboard/chunks/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ metadata: { ...currentMetadata, tags: [...tags, tag] } })
        });
        fetchChunks();
      } catch (err) {
        alert("Erreur lors de l'ajout du tag");
      }
    }
  };

  if (loading) return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Chargement...</div>;

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
            <div className="ml-4 border-l border-gray-700 pl-6 flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm font-bold text-white">{user?.fullName || "Lead Dev"}</div>
                <div className="text-xs text-gray-400">Admin</div>
              </div>
              <UserButton appearance={{ elements: { userButtonAvatarBox: "w-10 h-10" } }} />
            </div>
          </div>
        </header>

        <div className="grid gap-6">
          {chunks.map(chunk => (
            <div key={chunk.id} className="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow-lg">
              {/* En-tête de la carte avec Badges et Boutons */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  {chunk.status === 'PROPOSED' && <span className="flex items-center gap-1 text-yellow-400 bg-yellow-400/10 px-3 py-1 rounded-full text-sm font-medium"><Clock size={16}/> En attente</span>}
                  {chunk.status === 'TRUSTED' && <span className="flex items-center gap-1 text-green-400 bg-green-400/10 px-3 py-1 rounded-full text-sm font-medium"><CheckCircle size={16}/> Validé</span>}
                  {chunk.status === 'REJECTED' && <span className="flex items-center gap-1 text-red-400 bg-red-400/10 px-3 py-1 rounded-full text-sm font-medium"><XCircle size={16}/> Rejeté</span>}
                  <span className="text-gray-500 text-sm">
                    {chunk.created_at ? format(new Date(chunk.created_at), 'dd MMM yyyy', { locale: fr }) : ''}
                  </span>
                </div>
                
                <div className="flex gap-2">
                  {chunk.status !== 'TRUSTED' && (
                    <button onClick={() => updateStatus(chunk.id, 'TRUSTED')} className="bg-green-500/20 text-green-400 hover:bg-green-500/30 px-3 py-1.5 rounded transition-colors text-sm font-medium">
                      Accepter
                    </button>
                  )}
                  {chunk.status !== 'REJECTED' && (
                    <button onClick={() => updateStatus(chunk.id, 'REJECTED')} className="bg-red-500/20 text-red-400 hover:bg-red-500/30 px-3 py-1.5 rounded transition-colors text-sm font-medium">
                      Rejeter
                    </button>
                  )}
                </div>
              </div>

              {/* Contenu du code */}
              <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-gray-300 whitespace-pre-wrap border border-gray-800">
                {chunk.content}
              </div>

              {/* Tags */}
              <div className="mt-4 flex flex-wrap gap-2 items-center">
                <button 
                  onClick={() => addTag(chunk.id, chunk.metadata)}
                  className="flex items-center gap-1 text-gray-400 hover:text-white bg-gray-700/50 hover:bg-gray-700 px-2 py-1 rounded text-xs transition-colors"
                >
                  <Tag size={14} /> Ajouter un tag
                </button>
                {chunk.metadata?.tags?.map((tag, idx) => (
                  <span key={idx} className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-xs font-medium">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
          
          {chunks.length === 0 && (
            <div className="text-center py-20 text-gray-500">
              Le cerveau est vide. Utilisez "wechat-agent learn" pour ajouter de la mémoire.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <>
      <SignedOut>
        <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center text-white p-4">
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
        <DashboardContent />
      </SignedIn>
    </>
  );
}
