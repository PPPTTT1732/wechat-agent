# 🤖 WeChat Engineering Agent — AgentOps Platform

> **Plateforme d'intelligence artificielle hybride pour les équipes d'ingénierie WeChat.**
> Le Cloud gère la mémoire collective. L'IA de votre éditeur fait le vrai travail. Zéro coût d'API LLM.

---

## 📖 Table des Matières

1. [C'est quoi cette plateforme ?](#-cest-quoi-cette-plateforme-)
2. [Architecture du système](#-architecture-du-système)
3. [Installation pour un développeur](#-installation-pour-un-développeur)
4. [Flux de travail quotidien](#-flux-de-travail-quotidien-en-3-étapes)
5. [Référence des commandes CLI](#-référence-des-commandes-cli)
6. [Guide Admin (Déploiement)](#-guide-admin--déploiement--mise-à-jour)
7. [Variables d'environnement](#-variables-denvironnement)
8. [Architecture technique détaillée](#-architecture-technique-détaillée)
9. [FAQ & Dépannage](#-faq--dépannage)

---

## 🎯 C'est quoi cette plateforme ?

Le **WeChat Engineering Agent** est un système AgentOps conçu pour les équipes qui développent des mini-programmes WeChat (WeChat Native, Taro, etc.).

### Le problème qu'il résout
Quand un développeur bloque sur un bug ou doit ajouter une feature complexe, il perd du temps à :
- Expliquer le contexte à l'IA (stack technique, patterns utilisés, erreurs passées).
- Recommencer cette explication à chaque session.
- Dupliquer des solutions déjà trouvées par ses collègues.

### La solution
La plateforme joue le rôle d'un **Chef de Projet IA** qui connaît déjà votre codebase.

**En une commande**, elle prépare un cahier des charges complet (l'`ExecutionBrief`) que vous collez dans votre éditeur. L'IA de votre éditeur (Antigravity, Claude, Copilot...) peut alors coder directement sans que vous ayez à tout ré-expliquer.

Le résultat ? L'équipe va **2x à 3x plus vite** sur les tâches répétitives, et les solutions découvertes par un développeur sont automatiquement partagées avec le reste de l'équipe via la mémoire vectorielle.

---

## 🏗 Architecture du système

```
┌─────────────────────────────────────────────────────────────────┐
│                        VOTRE ORDINATEUR                          │
│                                                                   │
│   Terminal          Éditeur de Code (VSCode / Cursor)            │
│   ┌─────────┐       ┌────────────────────────────────────────┐   │
│   │  CLI    │──────▶│  Antigravity / Claude / Copilot        │   │
│   │wechat-  │       │                                        │   │
│   │agent    │       │  Lit le .wechat_brief.md               │   │
│   │prepare  │       │  et écrit le code directement          │   │
│   └────┬────┘       └────────────────────────────────────────┘   │
│        │                                                          │
└────────┼─────────────────────────────────────────────────────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD GRATUIT (Render.com)                    │
│                                                                   │
│   ┌──────────────┐    ┌─────────────────┐                        │
│   │  API FastAPI │    │  Worker Celery  │                        │
│   │  (Port 8000) │    │  (Asynchrone)   │                        │
│   └──────┬───────┘    └────────┬────────┘                        │
│          │                     │                                  │
└──────────┼─────────────────────┼──────────────────────────────── ┘
           │                     │
     ┌─────▼──────┐      ┌───────▼──────┐
     │   Neon DB  │      │    Upstash   │
     │ PostgreSQL │      │    Redis     │
     │ + pgvector │      │ (File tâche) │
     │  (Mémoire) │      └──────────────┘
     └────────────┘
```

**Règle d'or :** Le cloud ne fait jamais appel à un LLM externe payant. Il gère uniquement la mémoire partagée, les contrats et l'orchestration. **L'IA qui code reste sur votre machine, dans votre éditeur.**

---

## ⚡ Installation pour un développeur

> **Prérequis :** Python 3.11+, Git

### Étape 1 — Cloner le dépôt

```bash
git clone https://github.com/PPPTTT1732/wechat-agent.git
cd wechat-agent
```

### Étape 2 — Créer l'environnement virtuel et installer le CLI

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

### Étape 3 — Se connecter au serveur de l'équipe

```bash
.venv/bin/wechat-agent login
```

Le CLI vous demandera deux informations :
- **Token** : Demandez-le à votre Lead Dev ou Admin (ex: `DEV_TOKEN_ORG_A`)
- **URL du serveur** : `https://wechat-agent-5y0i.onrender.com`

### Étape 4 — Lier votre projet

Naviguez dans le dossier de votre mini-programme WeChat et lancez :

```bash
cd /chemin/vers/votre-projet-wechat
/chemin/vers/wechat-agent/.venv/bin/wechat-agent link
```

Le CLI vous demandera votre **Project ID** (ex: `mp-afritrips-v1`). Demandez-le à votre Admin.

✅ **Vous êtes prêt.** L'installation complète prend moins de 5 minutes.

---

## 🔄 Flux de travail quotidien en 3 étapes

> **Scénario :** Un développeur veut ajouter l'authentification WeChat Pay à la page de paiement.

### 1️⃣ `prepare` — Préparer le terrain

```bash
wechat-agent prepare "Intégrer WeChat Pay sur la page de paiement"
```

**Ce qui se passe :**
- Le CLI contacte le serveur Render.
- Le serveur cherche dans la base Neon si l'équipe a déjà résolu un problème similaire.
- Il génère un fichier `.wechat_brief.md` à la racine de votre projet.

**Durée :** ~3 secondes.

---

### 2️⃣ Coder avec votre IA — Donnez le Brief à l'IA de votre éditeur

Ouvrez le chat de votre éditeur (Antigravity, Claude, Copilot...) et dites simplement :

```
Exécute les instructions du fichier .wechat_brief.md
```

L'IA va lire le contexte complet (votre stack, les erreurs passées de l'équipe, les patterns utilisés dans le projet) et écrire le code directement dans les bons fichiers.

**Durée :** Variable selon la complexité.

---

### 3️⃣ `learn` — Partager la connaissance avec l'équipe

Quand l'IA a terminé et que vous avez validé le code :

```bash
wechat-agent learn
```

**Ce qui se passe :**
- Le CLI capture le `git diff` (les fichiers modifiés par l'IA).
- Il l'envoie au serveur Render pour vectorisation.
- Le serveur l'enregistre dans Neon avec le statut `PROPOSED`.
- Un Lead Dev valide la connaissance → elle passe en `TRUSTED` → elle est disponible pour toute l'équipe la prochaine fois.

---

## 📚 Référence des commandes CLI

### `wechat-agent login`
Configure la connexion au serveur de l'équipe.

```bash
wechat-agent login
# Options disponibles :
wechat-agent login --token MON_TOKEN --api-url https://serveur.onrender.com
```

| Option | Description | Défaut |
|--------|-------------|--------|
| `--token` | Votre token d'authentification d'équipe | (Demandé interactivement) |
| `--api-url` | URL du serveur AgentOps | `http://localhost:8000` |

---

### `wechat-agent link`
Lie le répertoire local à un projet dans la base de données.

```bash
wechat-agent link
# Option directe :
wechat-agent link --project-id mp-afritrips-v1
```

---

### `wechat-agent prepare`
Génère le fichier de contexte `.wechat_brief.md` pour l'IA de votre éditeur.

```bash
wechat-agent prepare "Votre demande en langage naturel"

# Exemples :
wechat-agent prepare "Ajouter la gestion d'erreur sur la page de paiement"
wechat-agent prepare "Créer un composant réutilisable pour les cartes de vol"
wechat-agent prepare "Refactoriser la logique de navigation pour Taro"
```

**Résultat :** Crée le fichier `.wechat_brief.md` à la racine du projet.

---

### `wechat-agent learn`
Capture le code modifié et l'envoie dans la mémoire partagée de l'équipe.

```bash
wechat-agent learn
```

**Important :** Lancez cette commande AVANT de faire `git commit`. La commande analyse les modifications non commitées (`git diff`).

---

## 🛠 Guide Admin — Déploiement & Mise à jour

### Mettre à jour le serveur

Tout push sur la branche `main` de GitHub déclenche automatiquement un redéploiement sur Render (si le déploiement automatique est activé dans Render).

```bash
# Pour déclencher un déploiement manuellement
git push origin main
```

### Configurer les variables d'environnement sur Render

Allez dans **Render > votre service > Environment** et vérifiez que ces variables sont présentes :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | URL de connexion Neon PostgreSQL | `postgresql://user:pass@host/db?sslmode=require` |
| `REDIS_URL` | URL de connexion Upstash Redis | `rediss://default:token@host:6379` |

### Ajouter un nouveau développeur à l'équipe

1. Invitez-le sur GitHub (Settings > Collaborators).
2. Donnez-lui le token d'équipe et l'URL Render.
3. Il suit le guide **Installation** (5 minutes).

### Migrations de base de données

Si vous modifiez les modèles SQLAlchemy (`packages/database/models.py`) :

```bash
cd /chemin/vers/wechat-agent
source .venv/bin/activate
alembic revision --autogenerate -m "description de la migration"
alembic upgrade head
```

---

## 🔐 Variables d'environnement

Créez un fichier `.env` à la racine du projet (copiez `.env.example`) :

```bash
cp .env.example .env
```

| Variable | Obligatoire | Description |
|----------|-------------|-------------|
| `DATABASE_URL` | ✅ | URL PostgreSQL (Neon) |
| `REDIS_URL` | ✅ | URL Redis (Upstash, commence par `rediss://`) |
| `OPENAI_API_KEY` | ❌ | Clé OpenAI (non requise avec le workflow hybride) |
| `ANTHROPIC_API_KEY` | ❌ | Clé Anthropic (non requise avec le workflow hybride) |

> ⚠️ **Ne commitez jamais votre fichier `.env` sur GitHub.** Il est déjà dans le `.gitignore`.

---

## 🏛 Architecture technique détaillée

### Les 5 contrats fondamentaux (Pydantic)

Toute la communication entre les composants utilise ces structures JSON strictes :

| Contrat | Description | Fichier |
|---------|-------------|---------|
| `TaskRequest` | La demande du développeur | `packages/agent_core/contracts.py` |
| `ExecutionBrief` | Le cahier des charges pour l'IA | `packages/agent_core/contracts.py` |
| `WorkerResult` | Le résultat du travail de l'IA | `packages/agent_core/contracts.py` |
| `ReviewResult` | Le verdict de l'Évaluateur | `packages/agent_core/contracts.py` |
| `LearningEvent` | La leçon à enregistrer en mémoire | `packages/agent_core/contracts.py` |

### Les 3 niveaux de connaissance (RAG Multi-Tenant)

Le système de recherche vectorielle respecte une hiérarchie stricte de visibilité :

```
Niveau 1 (Global)       → Connaissance publique WeChat (Fournie par la plateforme)
                           Accessible par TOUTES les organisations

Niveau 2 (Organisation) → Connaissance privée de votre équipe
                           Accessible uniquement par VOTRE organisation

Niveau 3 (Projet)       → Connaissance ultra-spécifique à UN projet
                           Accessible uniquement par les membres de CE projet
```

### Le Pipeline de Confiance

Aucune connaissance n'est jamais ajoutée directement en "trusted". Le cycle de vie d'une leçon :

```
PROPOSED → OBSERVED → VALIDATED → TRUSTED → SHARED
```

- **PROPOSED** : Ajouté automatiquement par `wechat-agent learn`
- **VALIDATED** : Approuvé par un Lead Dev dans l'interface admin
- **TRUSTED** : Disponible pour alimenter les futurs briefs de l'équipe

### Structure des dossiers

```
wechat-engineering-agent/
├── apps/
│   ├── api/               ← FastAPI (Routes HTTP)
│   │   ├── main.py
│   │   └── routers/
│   │       ├── projects.py  (CRUD des projets)
│   │       └── tasks.py     (Déclenchement des tâches)
│   ├── cli/               ← Outil développeur (wechat-agent)
│   │   └── main.py
│   └── worker/            ← Celery (Tâches asynchrones)
│       ├── celery_app.py
│       └── tasks.py
├── packages/
│   ├── agent_core/        ← Contrats Pydantic & Model Router
│   ├── code_intelligence/ ← Scanner statique de projet
│   ├── database/          ← Modèles SQLAlchemy & Migrations Alembic
│   ├── evaluator/         ← Agent Reviewer (Qualité du code)
│   ├── learning/          ← Moteur d'apprentissage
│   ├── memory/            ← RAG Retriever (Recherche vectorielle pgvector)
│   ├── providers/         ← Adaptateurs IA (OpenAI, Anthropic)
│   ├── prompts/           ← Tous les System Prompts
│   ├── security/          ← JWT & Multi-tenancy
│   └── wechat_specialist/ ← Agent Supervisor WeChat
├── docker/
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   └── render.Dockerfile  ← Image optimisée pour Render (gratuit)
├── docker-compose.yml     ← Pour le développement local
├── start.sh               ← Script de démarrage 2-en-1 (Render)
└── .env.example           ← Modèle de configuration
```

---

## ❓ FAQ & Dépannage

### Le serveur Render met 50 secondes à répondre le matin

C'est normal. Sur le plan gratuit, le serveur "s'endort" après 15 minutes d'inactivité. La première requête le réveille. Pour éviter ça, passez au plan payant ($7/mois) ou passez sur Oracle Cloud Always Free.

---

### `wechat-agent prepare` répond "Aucune mémoire trouvée"

C'est le comportement attendu lors de la **première utilisation** d'un projet. La mémoire se construit progressivement grâce à `wechat-agent learn`. Plus vous l'utilisez, plus il devient intelligent sur votre projet.

---

### La commande `wechat-agent` est introuvable

Vérifiez que vous utilisez bien le binaire dans votre environnement virtuel :

```bash
# Mauvais ❌
wechat-agent prepare "..."

# Bon ✅ (depuis la racine du dossier wechat-agent)
.venv/bin/wechat-agent prepare "..."

# Ou ajoutez le venv à votre PATH pour plus de confort
export PATH="/chemin/vers/wechat-agent/.venv/bin:$PATH"
```

---

### Comment lancer la plateforme en local (mode dev) ?

```bash
# Démarrer l'API et le Worker en local avec Docker
docker-compose up --build

# L'API est accessible sur http://localhost:8000
# La documentation interactive est sur http://localhost:8000/docs
```

---

### Comment voir les logs du serveur Render ?

1. Allez sur [render.com](https://render.com)
2. Sélectionnez votre service `wechat-agent`
3. Cliquez sur l'onglet **Logs**

---

## 📞 Support

Pour toute question sur la plateforme, contactez le **Lead Dev** de votre organisation ou ouvrez une **Issue** sur GitHub.

---

*Documentation générée par le WeChat AgentOps Platform — Version 1.0.0*
