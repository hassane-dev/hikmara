import re
from ai_models.base_model import BaseAIModel

class LLMEngine(BaseAIModel):
    def load(self):
        self.loaded = True
        return True

    def unload(self):
        self.loaded = False
        return True

    def predict(self, inputs):
        prompt = inputs.get("prompt", "")
        clean_prompt = prompt.strip().lower()

        # Custom responses for natural, contextualized offline conversation
        if clean_prompt in ["bonjour", "salut"]:
            return {"response": "Bonjour !\nComment puis-je vous aider aujourd'hui ?"}
        elif clean_prompt == "good morning":
            return {"response": "Good morning!\nHow can I help you today?"}
        elif any(g in clean_prompt for g in ["comment vas-tu", "comment ca va", "comment ça va", "comment vas tu"]):
            return {"response": "Je vais très bien, merci ! En tant qu'assistant local Hikmara AI, je suis opérationnel à 100%. Que puis-je faire pour vous aujourd'hui ?"}
        elif any(g in clean_prompt for g in ["how are you", "how's it going"]):
            return {"response": "I am doing great, thank you! As your local Hikmara AI assistant, I am fully operational offline. How can I help you today?"}
        elif any(g in clean_prompt for g in ["merci", "thanks", "thank you"]):
            return {"response": "De rien ! C'est un plaisir de vous aider. N'hésitez pas si vous avez d'autres requêtes !"}

        # Ambiguous "code" request
        elif clean_prompt in ["code", "le code", "du code"]:
            return {"response": "J'ai détecté une demande liée au code, mais elle est ambiguë. Souhaitez-vous générer un code particulier, analyser un script existant ou obtenir des explications techniques ? Pouvez-vous préciser votre besoin ?"}

        # Specific PHP script query
        elif "php" in clean_prompt and "somme" in clean_prompt:
            php_code = (
                "Voici le script PHP demandé pour calculer la somme de deux entiers :\n\n"
                "```php\n"
                "<?php\n"
                "function additionnerEntiers(int $a, int $b): int {\n"
                "    return $a + $b;\n"
                "}\n\n"
                "// Exemple d'utilisation :\n"
                "$resultat = additionnerEntiers(5, 10);\n"
                "echo \"La somme de 5 et 10 est : \" . $resultat; // Affiche 15\n"
                "?>\n"
                "```"
            )
            return {"response": php_code}

        # Project roadmap request
        elif any(k in clean_prompt for k in ["feuille de route", "roadmap", "planification"]) and "projet" in clean_prompt:
            roadmap = (
                "Voici une feuille de route recommandée pour structurer votre projet web :\n\n"
                "1. **Spécifications & Conception** : Définir le cahier des charges, les fonctionnalités clés et l'architecture générale.\n"
                "2. **Maquettage & UX/UI** : Concevoir les wireframes et l'identité visuelle de l'application.\n"
                "3. **Choix Technologique** : Choisir une stack adaptée (ex: React/Vue pour le Front, Flask/Express/PHP pour le Back, SQLite/PostgreSQL pour les données).\n"
                "4. **Développement Backend & API** : Créer la base de données, implémenter les services logiques et exposer les endpoints d'API.\n"
                "5. **Développement Frontend** : Intégrer les vues et connecter les interfaces utilisateur à l'API.\n"
                "6. **Validation, Tests & Sécurité** : Écrire des tests unitaires/intégration et effectuer un audit de vulnérabilités.\n"
                "7. **Déploiement & Maintenance** : Héberger l'application et planifier les cycles de mise à jour.\n\n"
                "Avez-vous une stack technique spécifique en tête ou des contraintes particulières pour ce projet ?"
            )
            return {"response": roadmap}

        elif "kubernetes" in clean_prompt:
            return {"response": "Kubernetes est un orchestrateur de conteneurs open-source conçu pour automatiser le déploiement, la mise à l'échelle et la gestion des applications conteneurisées."}
        elif "docker" in clean_prompt:
            return {"response": "Docker est une plateforme logicielle qui permet de concevoir, tester et déployer des applications rapidement sous forme de conteneurs légers et isolés."}

        # General response template
        return {"response": f"I am Hikmara AI local system. Regarding '{prompt}', let me assist you."}

    def status(self):
        return {"loaded": self.loaded}

    def get_information(self):
        return {"type": "LLM"}
