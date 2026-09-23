import React from 'react'
import ReactDOM from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import App from './App.jsx'
import './index.css'

// La clé sera chargée depuis un fichier .env local
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* Si la clé n'est pas encore définie, on affiche un message d'aide, sinon on lance l'app */}
    {!PUBLISHABLE_KEY ? (
      <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-8">
        <h1 className="text-3xl font-bold mb-4 text-red-400">Configuration Requise</h1>
        <p>Il manque la clé Clerk (VITE_CLERK_PUBLISHABLE_KEY) dans votre fichier .env</p>
      </div>
    ) : (
      <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
        <App />
      </ClerkProvider>
    )}
  </React.StrictMode>,
)
