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
        if clean_prompt == "bonjour":
            return {"response": "Bonjour !\nComment puis-je vous aider aujourd'hui ?"}
        elif clean_prompt == "good morning":
            return {"response": "Good morning!\nHow can I help you today?"}
        elif any(g in clean_prompt for g in ["comment vas-tu", "comment ca va", "comment ça va"]):
            return {"response": "Je vais très bien, merci ! En tant qu'assistant local Hikmara AI, je suis opérationnel à 100%. Que puis-je faire pour vous aujourd'hui ?"}
        elif any(g in clean_prompt for g in ["how are you", "how's it going"]):
            return {"response": "I am doing great, thank you! As your local Hikmara AI assistant, I am fully operational offline. How can I help you today?"}
        elif any(g in clean_prompt for g in ["merci", "thanks", "thank you"]):
            return {"response": "De rien ! C'est un plaisir de vous aider. N'hésitez pas si vous avez d'autres requêtes !"}
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
