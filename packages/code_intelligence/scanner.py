import os
import json
from typing import Dict, Any

class ProjectScanner:
    """
    Phase 09: Code Intelligence Engine.
    Analyse statique du dépôt Git pour extraire son ADN (framework, dépendances, architecture)
    sans utiliser d'IA, afin de préparer un contexte déterministe pour le WeChat Specialist.
    """

    def _read_json(self, filepath: str) -> dict:
        """Helper pour lire un fichier JSON s'il existe."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def analyze_workspace(self, workspace_path: str) -> Dict[str, Any]:
        """
        Analyse physiquement les fichiers du dossier et retourne le contexte.
        """
        context = {
            "framework": "Unknown",
            "language": "JavaScript",
            "wechat_native": False,
            "dependencies": [],
            "architecture": "standard"
        }

        # 1. Analyse du package.json (Détection Taro / Vue / React / TS)
        pkg_json = self._read_json(os.path.join(workspace_path, "package.json"))
        if pkg_json:
            deps = pkg_json.get("dependencies", {})
            dev_deps = pkg_json.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}
            
            context["dependencies"] = list(all_deps.keys())
            
            # Identification du Framework
            if "@tarojs/taro" in all_deps:
                context["framework"] = "Taro (React/Vue)"
            elif "vue" in all_deps:
                context["framework"] = "Vue.js"
            
            # Identification du Langage
            if "typescript" in all_deps:
                context["language"] = "TypeScript"

        # 2. Analyse des fichiers spécifiques WeChat
        project_config = self._read_json(os.path.join(workspace_path, "project.config.json"))
        app_json = self._read_json(os.path.join(workspace_path, "app.json"))
        
        if project_config or app_json:
            context["wechat_native"] = True
            if context["framework"] == "Unknown":
                context["framework"] = "WeChat Native (WXML/WXSS/WXS)"

        # 3. Détection d'architecture (présence de dossiers spécifiques Redux/Pinia)
        src_path = os.path.join(workspace_path, "src")
        if os.path.exists(os.path.join(src_path, "store")) or os.path.exists(os.path.join(workspace_path, "store")):
            context["architecture"] = "State-Managed (Redux/Pinia/Vuex)"
        elif os.path.exists(os.path.join(src_path, "composables")):
            context["architecture"] = "Composition API (Vue)"

        return context

    def analyze_workspace_mock(self, repository_url: str) -> Dict[str, Any]:
        """
        Mock en attendant que l'étape de Git Clone soit implémentée.
        Renvoie une structure d'analyse typique de votre environnement.
        """
        return {
            "framework": "WeChat Native",
            "language": "JavaScript (ES5/WXS)",
            "wechat_native": True,
            "architecture": "WeChat Page/Component Architecture",
            "repository": repository_url
        }
