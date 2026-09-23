import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, Tag, Github } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { SignedIn, SignedOut, SignInButton, UserButton, useUser, useAuth } from '@clerk/clerk-react';

const API_URL = "https://wechat-agent-5y0i.onrender.com/api/v1/memory";
const PROJECT_ID = "mp-afritrips-v1";

function DashboardContent() {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [chunks, setChunks] = useState([]);
  const [role, setRole] = useState("DEV"); // Par défaut, tout le monde est dev
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const token = await getToken();
      const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
      
      // 1. Récupération du rôle
      const roleRes = await fetch(`${API_URL}/dashboard/me`, { headers });
      if (roleRes.ok) {
        const roleData = await roleRes.json();
        setRole(roleData.role);
      }

      // 2. Récupération de la mémoire
      const res = await fetch(`${API_URL}/dashboard/chunks?project_id=${PROJECT_ID}`, { headers });
      if (res.ok) {
        setChunks(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const updateStatus = async (id, newStatus) => {
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/dashboard/chunks/${id}`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      if (!res.ok) throw new Error("Accès refusé");
      fetchData();
    } catch (err) {
      alert(err.message);
    }
  };

  const addTag = async (id, currentMetadata) => {
    const tag = prompt("Entrez un tag (ex: navigation, api, ui):");
    if (!tag) return;
    
    const tags = currentMetadata?.tags || [];
    if (!tags.includes(tag)) {
      try {
        const token = await getToken();
        const res = await fetch(`${API_URL}/dashboard/chunks/${id}`, {
          method: 'PATCH',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ metadata: { ...currentMetadata, tags: [...tags, tag] } })
        });
        if (!res.ok) throw new Error("Accès refusé");
        fetchData();
      } catch (err) {
        alert(err.message);
      }
    }
  };

  if (loading) return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Sécurisation du Dashboard...</div>;

  const isAdmin = role === "ADMIN";

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
                <div className="text-sm font-bold text-white">{user?.fullName || "Utilisateur"}</div>
                {/* Affiche dynamiquement le rôle récupéré du serveur */}
                <div className={`text-xs font-bold ${isAdmin ? 'text-purple-400' : 'text-gray-500'}`}>
                  {isAdmin ? '👑 Lead Dev' : '💻 Développeur'}
                </div>
              </div>
              <UserButton appearance={{ elements: { userButtonAvatarBox: "w-10 h-10" } }} />
            </div>
          </div>
        </header>

        <div className="grid gap-6">
          {chunks.map(chunk => (
            <div key={chunk.id} className="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow-lg relative overflow-hidden">
              {!isAdmin && chunk.status === 'PROPOSED' && (
                <div className="absolute top-0 right-0 bg-yellow-500/20 text-yellow-300 text-xs px-3 py-1 rounded-bl-lg font-bold">
                  En attente de validation par le Lead Dev
                </div>
              )}
              
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3 mt-2">
                  {chunk.status === 'PROPOSED' && <span className="flex items-center gap-1 text-yellow-400 bg-yellow-400/10 px-3 py-1 rounded-full text-sm font-medium"><Clock size={16}/> En attente</span>}
                  {chunk.status === 'TRUSTED' && <span className="flex items-center gap-1 text-green-400 bg-green-400/10 px-3 py-1 rounded-full text-sm font-medium"><CheckCircle size={16}/> Validé</span>}
                  {chunk.status === 'REJECTED' && <span className="flex items-center gap-1 text-red-400 bg-red-400/10 px-3 py-1 rounded-full text-sm font-medium"><XCircle size={16}/> Rejeté</span>}
                  <span className="text-gray-500 text-sm">
                    {chunk.created_at ? format(new Date(chunk.created_at), 'dd MMM yyyy', { locale: fr }) : ''}
                  </span>
                </div>
                
                {/* Les boutons ne s'affichent QUE pour l'Admin */}
                {isAdmin && (
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
                )}
              </div>

              <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-gray-300 whitespace-pre-wrap border border-gray-800">
                {chunk.content}
              </div>

              {isAdmin && (
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
              )}
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
