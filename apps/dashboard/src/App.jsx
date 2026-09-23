import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, Tag, Github, Plus, Image as ImageIcon, Copy } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { SignedIn, SignedOut, SignInButton, UserButton, useUser, useAuth } from '@clerk/clerk-react';

const API_URL = "https://wechat-agent-5y0i.onrender.com/api/v1/memory";
const PROJECT_ID = "mp-afritrips-v1";
const CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/qudmvipg/image/upload";
const CLOUDINARY_PRESET = "wechat";

function DashboardContent() {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [chunks, setChunks] = useState([]);
  const [role, setRole] = useState("DEV");
  const [loading, setLoading] = useState(true);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [newCode, setNewCode] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  const fetchData = async () => {
    try {
      const token = await getToken();
      const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
      
      const roleRes = await fetch(`${API_URL}/dashboard/me`, { headers });
      if (roleRes.ok) setRole((await roleRes.json()).role);

      const res = await fetch(`${API_URL}/dashboard/chunks?project_id=${PROJECT_ID}`, { headers });
      if (res.ok) setChunks(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const isAdmin = role === "ADMIN";

  const updateStatus = async (id, newStatus) => {
    try {
      const token = await getToken();
      await fetch(`${API_URL}/dashboard/chunks/${id}`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchData();
    } catch (err) { alert(err.message); }
  };

  const handlePublish = async (e) => {
    e.preventDefault();
    if (!newCode) return;
    setUploading(true);

    try {
      let imageUrl = null;
      
      // 1. Upload Cloudinary (si une image est sélectionnée)
      if (selectedFile) {
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("upload_preset", CLOUDINARY_PRESET);
        
        const uploadRes = await fetch(CLOUDINARY_URL, { method: "POST", body: formData });
        const uploadData = await uploadRes.json();
        if (uploadData.secure_url) {
          imageUrl = uploadData.secure_url;
        } else {
          console.error("Erreur Cloudinary:", uploadData);
          alert("Assurez-vous que l'Upload Preset 'wechat' est en mode 'Unsigned' dans Cloudinary.");
        }
      }

      // 2. Envoi au Backend FastAPI
      const token = await getToken();
      const payload = {
        content: newCode,
        project_id: PROJECT_ID,
        metadata: { type: "component", image_url: imageUrl, author: user?.fullName, tags: ["UI"] }
      };

      await fetch(`${API_URL}/learn`, {
        method: "POST",
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      setIsModalOpen(false);
      setNewCode("");
      setSelectedFile(null);
      fetchData(); // Rafraîchir la liste
    } catch (err) {
      console.error(err);
      alert("Erreur lors de la publication.");
    } finally {
      setUploading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert("Code copié dans le presse-papier !");
  };

  if (loading) return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Initialisation du Hub...</div>;

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10 flex justify-between items-center bg-[#111111] p-6 rounded-2xl border border-[#262626]">
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
              UI Component Hub
            </h1>
            <p className="text-gray-400 mt-2">Design System & Gouvernance pour {PROJECT_ID}</p>
          </div>
          <div className="flex gap-6 items-center">
            <button 
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white px-5 py-2.5 rounded-lg font-bold transition-all shadow-[0_0_15px_rgba(124,58,237,0.3)]"
            >
              <Plus size={20} /> Publier un composant
            </button>
            <div className="h-10 w-px bg-gray-800"></div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm font-bold text-white">{user?.fullName || "Utilisateur"}</div>
                <div className={`text-xs font-bold ${isAdmin ? 'text-purple-400' : 'text-gray-500'}`}>
                  {isAdmin ? '👑 Lead Dev' : '💻 Développeur'}
                </div>
              </div>
              <UserButton appearance={{ elements: { userButtonAvatarBox: "w-10 h-10" } }} />
            </div>
          </div>
        </header>

        {/* Modal de Publication */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-[#111111] border border-[#262626] p-8 rounded-2xl w-full max-w-2xl shadow-2xl">
              <h2 className="text-2xl font-bold mb-6 text-white">Publier un nouveau composant</h2>
              <form onSubmit={handlePublish}>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-400 mb-2">Code du composant (WXML/WXSS/JS)</label>
                  <textarea 
                    value={newCode}
                    onChange={(e) => setNewCode(e.target.value)}
                    className="w-full h-40 bg-black border border-gray-800 rounded-lg p-4 text-sm font-mono text-gray-300 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    placeholder="<!-- Collez votre code WeChat ici -->"
                    required
                  ></textarea>
                </div>
                
                <div className="mb-8">
                  <label className="block text-sm font-medium text-gray-400 mb-2">Aperçu visuel (Capture d'écran)</label>
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-800 border-dashed rounded-lg cursor-pointer bg-black/50 hover:bg-gray-900 transition-colors">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <ImageIcon className="w-8 h-8 mb-3 text-gray-500" />
                      <p className="text-sm text-gray-400">
                        {selectedFile ? <span className="text-purple-400 font-bold">{selectedFile.name}</span> : "Cliquez pour sélectionner une image (PNG/JPG)"}
                      </p>
                    </div>
                    <input type="file" className="hidden" accept="image/*" onChange={(e) => setSelectedFile(e.target.files[0])} />
                  </label>
                </div>

                <div className="flex justify-end gap-4">
                  <button type="button" onClick={() => setIsModalOpen(false)} className="px-5 py-2.5 text-gray-400 hover:text-white transition-colors font-medium">Annuler</button>
                  <button type="submit" disabled={uploading} className="bg-white text-black px-6 py-2.5 rounded-lg font-bold hover:bg-gray-200 transition-colors disabled:opacity-50 flex items-center gap-2">
                    {uploading ? "Envoi vers le Cloud..." : "Publier dans le Cerveau"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Grille des Composants */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {chunks.map(chunk => (
            <div key={chunk.id} className="bg-[#111111] border border-[#262626] rounded-xl overflow-hidden shadow-lg group">
              {/* Image Cloudinary */}
              {chunk.metadata?.image_url ? (
                <div className="w-full h-64 bg-black border-b border-[#262626] overflow-hidden relative">
                  <img src={chunk.metadata.image_url} alt="Composant" className="w-full h-full object-cover object-top opacity-80 group-hover:opacity-100 transition-opacity" />
                </div>
              ) : (
                <div className="w-full h-24 bg-gradient-to-r from-gray-900 to-black border-b border-[#262626] flex items-center justify-center">
                  <span className="text-gray-700 text-sm font-mono">Aucun aperçu disponible</span>
                </div>
              )}
              
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    {chunk.status === 'PROPOSED' && <span className="flex items-center gap-1 text-yellow-400 bg-yellow-400/10 px-3 py-1 rounded-full text-sm font-medium"><Clock size={16}/> En attente</span>}
                    {chunk.status === 'TRUSTED' && <span className="flex items-center gap-1 text-green-400 bg-green-400/10 px-3 py-1 rounded-full text-sm font-medium"><CheckCircle size={16}/> Validé</span>}
                    {chunk.status === 'REJECTED' && <span className="flex items-center gap-1 text-red-400 bg-red-400/10 px-3 py-1 rounded-full text-sm font-medium"><XCircle size={16}/> Rejeté</span>}
                    <span className="text-gray-500 text-sm">
                      {chunk.created_at ? format(new Date(chunk.created_at), 'dd MMM yyyy', { locale: fr }) : ''}
                    </span>
                  </div>
                  
                  {isAdmin && (
                    <div className="flex gap-2">
                      {chunk.status !== 'TRUSTED' && <button onClick={() => updateStatus(chunk.id, 'TRUSTED')} className="bg-green-500/20 text-green-400 hover:bg-green-500/30 px-3 py-1 rounded text-xs font-medium">Accepter</button>}
                      {chunk.status !== 'REJECTED' && <button onClick={() => updateStatus(chunk.id, 'REJECTED')} className="bg-red-500/20 text-red-400 hover:bg-red-500/30 px-3 py-1 rounded text-xs font-medium">Rejeter</button>}
                    </div>
                  )}
                </div>

                <div className="relative">
                  <div className="bg-[#050505] rounded-lg p-4 font-mono text-sm text-gray-300 whitespace-pre-wrap border border-[#262626] max-h-48 overflow-y-auto">
                    {chunk.content}
                  </div>
                  <button onClick={() => copyToClipboard(chunk.content)} className="absolute top-2 right-2 bg-gray-800 hover:bg-gray-700 text-white p-2 rounded-md transition-colors" title="Copier le code">
                    <Copy size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
          
          {chunks.length === 0 && (
            <div className="text-center py-20 text-gray-500 col-span-full">
              Le Hub est vide. Soyez le premier à publier un composant !
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
        <div className="min-h-screen bg-[#030712] flex flex-col items-center justify-center text-white p-4">
          <div className="bg-white/5 backdrop-blur-xl p-10 rounded-2xl shadow-2xl max-w-md w-full text-center border border-white/10 relative overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-32 bg-purple-500/30 blur-[50px] rounded-full pointer-events-none"></div>
            <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 relative z-10">
              AgentOps
            </h1>
            <p className="text-gray-400 mb-8 relative z-10">Le Hub de Composants & Intelligence</p>
            
            <SignInButton mode="modal">
              <button className="w-full flex items-center justify-center gap-3 bg-white text-gray-900 py-3 px-4 rounded-lg font-bold hover:bg-gray-100 transition-colors relative z-10">
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
