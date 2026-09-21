#!/bin/bash
# ============================================================
# 🤖 WeChat Engineering Agent — Installateur Automatique
# ============================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   WeChat Engineering Agent — Install    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Vérification de Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Python 3 est requis. Installez-le sur python.org${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 trouvé${NC}"

# Dossier d'installation
INSTALL_DIR="$HOME/.wechat-agent-bin"
mkdir -p "$INSTALL_DIR"

# Clonage ou mise à jour du dépôt
REPO_DIR="$INSTALL_DIR/wechat-engineering-agent"
if [ -d "$REPO_DIR" ]; then
    echo -e "${YELLOW}🔄 Mise à jour du CLI...${NC}"
    cd "$REPO_DIR" && git pull --quiet
else
    echo -e "${YELLOW}📥 Téléchargement du CLI...${NC}"
    git clone --quiet https://github.com/PPPTTT1732/wechat-agent.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

# Création de l'environnement Python isolé
echo -e "${YELLOW}🐍 Création de l'environnement Python...${NC}"
python3 -m venv "$INSTALL_DIR/venv" --quiet

# Installation des dépendances
echo -e "${YELLOW}📦 Installation des dépendances...${NC}"
"$INSTALL_DIR/venv/bin/pip" install -e "$REPO_DIR" --quiet

# Création du wrapper global (accessible depuis n'importe où)
WRAPPER_PATH="/usr/local/bin/wechat-agent"
if [ -w "/usr/local/bin" ]; then
    # On a les droits d'écriture (Linux standard)
    cat << WRAPPER > "$WRAPPER_PATH"
#!/bin/bash
exec "$INSTALL_DIR/venv/bin/wechat-agent" "\$@"
WRAPPER
    chmod +x "$WRAPPER_PATH"
else
    # Sinon, on l'ajoute dans ~/.local/bin (ne demande pas sudo)
    mkdir -p "$HOME/.local/bin"
    WRAPPER_PATH="$HOME/.local/bin/wechat-agent"
    cat << WRAPPER > "$WRAPPER_PATH"
#!/bin/bash
exec "$INSTALL_DIR/venv/bin/wechat-agent" "\$@"
WRAPPER
    chmod +x "$WRAPPER_PATH"
    # S'assurer que ~/.local/bin est dans le PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
        export PATH="$HOME/.local/bin:$PATH"
    fi
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Installation réussie !              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "La commande ${YELLOW}wechat-agent${NC} est maintenant disponible."
echo ""
echo -e "${BLUE}🚀 Prochaine étape : Connectez-vous${NC}"
echo -e "   ${YELLOW}wechat-agent login${NC}"
echo ""
echo -e "${BLUE}📋 Puis préparez votre premier brief :${NC}"
echo -e "   ${YELLOW}wechat-agent prepare \"Votre demande ici\"${NC}"
echo ""
