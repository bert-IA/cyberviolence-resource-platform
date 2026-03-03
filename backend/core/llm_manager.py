"""
Gestionnaire LLM indépendant et configurable
Supporte multiple providers avec gestion d'erreurs robuste
"""
import os
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Imports conditionnels pour éviter les erreurs de dépendances
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    GEMINI = "gemini"
    OPENROUTER = "openrouter" 
    # LOCAL supprimé - ne plus utiliser les données codées en dur

@dataclass
class LLMConfig:
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 1000
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass 
class LLMResponse:
    success: bool
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    error: Optional[str] = None

class BaseLLMClient(ABC):
    """Interface abstraite pour tous les clients LLM"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.api_key = config.api_key or self._get_api_key()
        
    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """Récupère la clé API depuis l'environnement"""
        pass
    
    @abstractmethod
    def _make_request(self, prompt: str) -> LLMResponse:
        """Effectue la requête vers le provider LLM"""
        pass
    
    def test_connection(self) -> bool:
        """Test la connexion au LLM (peut être surchargée)"""
        test_prompt = "Répondre uniquement par 'OK' si vous recevez ce message."
        response = self.generate(test_prompt)
        
        if response.success and "OK" in response.content.upper():
            logger.info(f"LLM {self.config.provider.value} connexion OK")
            return True
        else:
            logger.error(f"LLM {self.config.provider.value} connexion FAILED: {response.error}")
            return False
    
    def generate(self, prompt: str) -> LLMResponse:
        """Génère une réponse avec retry logic et gestion rate limiting"""
        start_time = time.time()
        
        for attempt in range(self.config.max_retries):
            try:
                response = self._make_request(prompt)
                response.response_time = time.time() - start_time
                return response
                
            except Exception as e:
                error_str = str(e)
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries - 1:
                    # Délai plus long pour les erreurs 429 (rate limiting)
                    if "429" in error_str or "Too Many Requests" in error_str:
                        delay = 60.0 * (attempt + 1)  # 60s, 120s, 180s pour rate limiting très agressif
                        logger.info(f"Rate limiting détecté, attente {delay}s avant retry")
                        time.sleep(delay)
                    else:
                        time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    return LLMResponse(
                        success=False,
                        content="",
                        provider=self.config.provider.value,
                        model=self.config.model,
                        error=str(e),
                        response_time=time.time() - start_time
                    )

class GeminiClient(BaseLLMClient):
    """Client pour Google Gemini"""
    
    def _get_api_key(self) -> Optional[str]:
        return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    def _make_request(self, prompt: str) -> LLMResponse:
        try:
            import google.generativeai as genai
            
            if not self.api_key:
                raise ValueError("Clé API Gemini manquante")
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.config.model)
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                )
            )
            
            # Récupérer les tokens utilisés de manière sécurisée
            tokens_used = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                tokens_used = getattr(response.usage_metadata, 'total_token_count', None)
            
            return LLMResponse(
                success=True,
                content=response.text,
                provider=self.config.provider.value,
                model=self.config.model,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            raise Exception(f"Erreur Gemini: {e}")

class OpenRouterClient(BaseLLMClient):
    """Client pour OpenRouter"""
    
    def _get_api_key(self) -> Optional[str]:
        return os.environ.get("OPENROUTER_API_KEY")
    
    def _make_request(self, prompt: str) -> LLMResponse:
        try:
            import requests
            
            if not self.api_key:
                raise ValueError("Clé API OpenRouter manquante")
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=data, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens")
            
            return LLMResponse(
                success=True,
                content=content,
                provider=self.config.provider.value,
                model=self.config.model,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            raise Exception(f"Erreur OpenRouter: {e}")

# ============================================================================
# LLM MANAGER
# ============================================================================

class LLMManager:
    """Gestionnaire principal pour tous les LLM"""
    
    PROVIDER_CLIENTS = {
        LLMProvider.GEMINI: GeminiClient,
        LLMProvider.OPENROUTER: OpenRouterClient,
    }
    
    DEFAULT_CONFIGS = {
        LLMProvider.GEMINI: LLMConfig(
            provider=LLMProvider.GEMINI,
            model="gemini-2.5-flash",
            temperature=0.0,
            max_tokens=8192  # gemini-2.5-flash est un modèle "thinking" :
                             # il consomme des tokens pour raisonner en interne
                             # AVANT de produire la réponse visible.
                             # Avec max_tokens=1000 → ~860 tokens de pensée
                             # + seulement ~140 tokens de réponse → troncature.
                             # 8192 donne assez de marge pour les deux.
        ),
        LLMProvider.OPENROUTER: LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model="meta-llama/llama-3.2-3b-instruct:free",
            temperature=0.0,
            max_tokens=2000
        ),
    }
    
    def __init__(self, provider: LLMProvider = LLMProvider.GEMINI, custom_config: Optional[LLMConfig] = None):
        self.provider = provider
        self.config = custom_config or self.DEFAULT_CONFIGS[provider]
        self.client = self._create_client()
        self._stats = {"requests": 0, "successes": 0, "failures": 0}
    
    def _create_client(self) -> BaseLLMClient:
        """Crée le client LLM approprié"""
        client_class = self.PROVIDER_CLIENTS[self.provider]
        return client_class(self.config)
    
    def generate(self, prompt: str, override_config: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Génère une réponse avec le LLM configuré"""
        self._stats["requests"] += 1
        
        # Override temporaire de config si fourni
        if override_config:
            temp_config = LLMConfig(**{**self.config.__dict__, **override_config})
            temp_client = self.PROVIDER_CLIENTS[self.provider](temp_config)
            response = temp_client.generate(prompt)
        else:
            response = self.client.generate(prompt)
        
        if response.success:
            self._stats["successes"] += 1
        else:
            self._stats["failures"] += 1
        
        return response
    
    def switch_provider(self, new_provider: LLMProvider, custom_config: Optional[LLMConfig] = None):
        """Change de provider LLM à la volée"""
        self.provider = new_provider
        self.config = custom_config or self.DEFAULT_CONFIGS[new_provider]
        self.client = self._create_client()
        logger.info(f"LLM Provider changé vers: {new_provider.value}")
    
    def test_connection(self) -> bool:
        """Test la connexion au LLM via le client"""
        return self.client.test_connection()
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques d'utilisation du LLM"""
        success_rate = (self._stats["successes"] / self._stats["requests"]) * 100 if self._stats["requests"] > 0 else 0
        
        return {
            **self._stats,
            "success_rate": round(success_rate, 2),
            "current_provider": self.provider.value,
            "current_model": self.config.model
        }

# Instance singleton par défaut
_default_llm_manager = None

def get_llm_manager(provider: LLMProvider = LLMProvider.GEMINI) -> LLMManager:
    """Récupère l'instance singleton du gestionnaire LLM"""
    global _default_llm_manager
    if _default_llm_manager is None:
        _default_llm_manager = LLMManager(provider)
    return _default_llm_manager

def create_llm_manager(provider: LLMProvider, custom_config: Optional[LLMConfig] = None) -> LLMManager:
    """Crée une nouvelle instance du gestionnaire LLM (non-singleton)"""
    return LLMManager(provider, custom_config)