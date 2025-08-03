"""
LLM Manager - Supports multiple AI models with automatic fallback
"""

import os
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from langchain_core.language_models.base import BaseLanguageModel

"""
LLM Manager - Supports multiple AI models with automatic fallback
"""

import os
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from langchain_core.language_models.base import BaseLanguageModel

# Import core LangChain LLM providers with fallbacks
from langchain_openai import ChatOpenAI

try:
    from langchain_openai import AzureChatOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False

# Optional imports for additional providers
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from langchain_mistralai import ChatMistralAI
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

try:
    from langchain_community.llms import Ollama
    from langchain_community.chat_models import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from langchain_cohere import ChatCohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

try:
    from langchain_fireworks import ChatFireworks
    FIREWORKS_AVAILABLE = True
except ImportError:
    FIREWORKS_AVAILABLE = False

try:
    from langchain_together import ChatTogether
    TOGETHER_AVAILABLE = True
except ImportError:
    TOGETHER_AVAILABLE = False

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


@dataclass
class ModelConfig:
    """Configuration for a language model."""
    provider: str
    model_name: str
    api_key_env: str
    base_url_env: Optional[str] = None
    default_model: str = None
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    enabled: bool = True


class LLMManager:
    """Manages multiple language model providers with automatic fallback."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._current_llm = None
        self._available_models: List[ModelConfig] = []
        self._setup_model_configs()
    
    def _setup_model_configs(self):
        """Setup model configurations based on available providers and user environment."""
        self._available_models = []
        
        # OpenAI models - user-specified only
        openai_models_env = os.getenv("OPENAI_MODELS")
        if openai_models_env:
            openai_models = openai_models_env.split(",")
            for model in openai_models:
                model = model.strip()
                if model:
                    self._available_models.append(
                        ModelConfig(
                            provider="openai",
                            model_name=model,
                            api_key_env="OPENAI_API_KEY",
                            base_url_env="OPENAI_BASE_URL",
                            default_model=model
                        )
                    )
        
        # Anthropic models - user-specified only
        if ANTHROPIC_AVAILABLE:
            anthropic_models_env = os.getenv("ANTHROPIC_MODELS")
            if anthropic_models_env:
                anthropic_models = anthropic_models_env.split(",")
                for model in anthropic_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                                provider="anthropic",
                                model_name=model,
                                api_key_env="ANTHROPIC_API_KEY",
                                default_model=model
                            )
                        )
        
        # Google models - user-specified only
        if GOOGLE_AVAILABLE:
            google_models_env = os.getenv("GOOGLE_MODELS")
            if google_models_env:
                google_models = google_models_env.split(",")
                for model in google_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                                provider="google",
                                model_name=model,
                                api_key_env="GOOGLE_API_KEY",
                                default_model=model
                            )
                        )
        
        # Mistral models - user-specified only
        if MISTRAL_AVAILABLE:
            mistral_models_env = os.getenv("MISTRAL_MODELS")
            if mistral_models_env:
                mistral_models = mistral_models_env.split(",")
                for model in mistral_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                                provider="mistral",
                                model_name=model,
                                api_key_env="MISTRAL_API_KEY",
                                default_model=model
                            )
                        )
        
        # Groq models - user-specified only
        if GROQ_AVAILABLE:
            groq_models_env = os.getenv("GROQ_MODELS")
            if groq_models_env:
                groq_models = groq_models_env.split(",")
                for model in groq_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                                provider="groq",
                                model_name=model,
                                api_key_env="GROQ_API_KEY",
                                default_model=model
                            )
                        )
        
        # Together AI models - user-specified only
        if TOGETHER_AVAILABLE:
            together_models_env = os.getenv("TOGETHER_MODELS")
            if together_models_env:
                together_models = together_models_env.split(",")
                for model in together_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                                provider="together",
                                model_name=model,
                                api_key_env="TOGETHER_API_KEY",
                                default_model=model
                            )
                        )
        
        # Cohere models - user-specified only
        if COHERE_AVAILABLE:
            cohere_models_env = os.getenv("COHERE_MODELS")
            if cohere_models_env:
                cohere_models = cohere_models_env.split(",")
                for model in cohere_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                                provider="cohere",
                                model_name=model,
                                api_key_env="COHERE_API_KEY",
                                default_model=model
                            )
                        )
        
        # Fireworks models - user-specified only
        if FIREWORKS_AVAILABLE:
            fireworks_models_env = os.getenv("FIREWORKS_MODELS")
            if fireworks_models_env:
                fireworks_models = fireworks_models_env.split(",")
                for model in fireworks_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                                provider="fireworks",
                                model_name=model,
                                api_key_env="FIREWORKS_API_KEY",
                                default_model=model
                            )
                        )
        
        # Local Ollama models - user-specified only
        if OLLAMA_AVAILABLE:
            ollama_models_env = os.getenv("OLLAMA_MODELS")
            if ollama_models_env:
                ollama_models = ollama_models_env.split(",")
                for model in ollama_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                            provider="ollama",
                            model_name=model,
                            api_key_env="",  # No API key needed
                            base_url_env="OLLAMA_BASE_URL",
                            default_model=model
                        )
                    )
        
        # Azure OpenAI models - user-specified only
        if AZURE_OPENAI_AVAILABLE:
            azure_models_env = os.getenv("AZURE_OPENAI_MODELS")
            if azure_models_env:
                azure_models = azure_models_env.split(",")
                for model in azure_models:
                    model = model.strip()
                    if model:
                        self._available_models.append(
                            ModelConfig(
                                provider="azure_openai",
                                model_name=model,
                            api_key_env="AZURE_OPENAI_API_KEY",
                            base_url_env="AZURE_OPENAI_ENDPOINT",
                            default_model=model
                        )
                    )
        
        # Custom OpenAI-compatible endpoint - user-specified only
        custom_models_env = os.getenv("CUSTOM_MODELS")
        if custom_models_env:
            custom_models = custom_models_env.split(",")
            for model in custom_models:
                model = model.strip()
                if model:
                    self._available_models.append(
                        ModelConfig(
                        provider="custom_openai",
                        model_name=model,
                        api_key_env="CUSTOM_API_KEY",
                        base_url_env="CUSTOM_BASE_URL",
                        default_model=model
                    )
                )
    
    def _is_model_available(self, config: ModelConfig) -> bool:
        """Check if a model configuration is available."""
        if not config.enabled:
            return False
        
        # For Ollama, check if service is running
        if config.provider == "ollama":
            base_url = os.getenv(config.base_url_env) or "http://localhost:11434"
            try:
                import requests
                response = requests.get(f"{base_url}/api/tags", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # For custom_openai, check if user has configured it
        if config.provider == "custom_openai":
            api_key = os.getenv(config.api_key_env)
            base_url = os.getenv(config.base_url_env)
            return api_key is not None and api_key.strip() != "" and base_url is not None and base_url.strip() != ""
        
        # For Azure OpenAI, check both API key and endpoint
        if config.provider == "azure_openai":
            api_key = os.getenv(config.api_key_env)
            endpoint = os.getenv(config.base_url_env)
            return api_key is not None and api_key.strip() != "" and endpoint is not None and endpoint.strip() != ""
        
        # For API-based models, check if API key is available
        if config.api_key_env:
            api_key = os.getenv(config.api_key_env)
            return api_key is not None and api_key.strip() != ""
        
        return True
    
    def _create_llm_from_config(self, config: ModelConfig) -> Optional[BaseLanguageModel]:
        """Create an LLM instance from configuration."""
        try:
            common_params = {
                "temperature": config.temperature,
                "model": config.default_model or config.model_name,
            }
            
            if config.max_tokens:
                common_params["max_tokens"] = config.max_tokens
            
            if config.provider == "openai":
                api_key = os.getenv(config.api_key_env)
                base_url = os.getenv(config.base_url_env)
                return ChatOpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    **common_params
                )
            
            elif config.provider == "anthropic" and ANTHROPIC_AVAILABLE:
                api_key = os.getenv(config.api_key_env)
                return ChatAnthropic(
                    api_key=api_key,
                    **common_params
                )
            
            elif config.provider == "google" and GOOGLE_AVAILABLE:
                api_key = os.getenv(config.api_key_env)
                return ChatGoogleGenerativeAI(
                    google_api_key=api_key,
                    **common_params
                )
            
            elif config.provider == "mistral" and MISTRAL_AVAILABLE:
                api_key = os.getenv(config.api_key_env)
                return ChatMistralAI(
                    api_key=api_key,
                    **common_params
                )
            
            elif config.provider == "groq" and GROQ_AVAILABLE:
                api_key = os.getenv(config.api_key_env)
                return ChatGroq(
                    api_key=api_key,
                    **common_params
                )
            
            elif config.provider == "together" and TOGETHER_AVAILABLE:
                api_key = os.getenv(config.api_key_env)
                return ChatTogether(
                    api_key=api_key,
                    **common_params
                )
            
            elif config.provider == "cohere" and COHERE_AVAILABLE:
                api_key = os.getenv(config.api_key_env)
                return ChatCohere(
                    cohere_api_key=api_key,
                    **common_params
                )
            
            elif config.provider == "fireworks" and FIREWORKS_AVAILABLE:
                api_key = os.getenv(config.api_key_env)
                return ChatFireworks(
                    api_key=api_key,
                    **common_params
                )
            
            elif config.provider == "ollama" and OLLAMA_AVAILABLE:
                base_url = os.getenv(config.base_url_env, "http://localhost:11434")
                return ChatOllama(
                    base_url=base_url,
                    **common_params
                )
            
            elif config.provider == "custom_openai":
                # Handle custom OpenAI-compatible endpoints (user configured)
                api_key = os.getenv(config.api_key_env)
                base_url = os.getenv(config.base_url_env)
                if not api_key or not base_url:
                    return None
                return ChatOpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    **common_params
                )
            
            elif config.provider == "azure_openai" and AZURE_OPENAI_AVAILABLE:
                # Handle Azure OpenAI
                api_key = os.getenv(config.api_key_env)
                endpoint = os.getenv(config.base_url_env)
                api_version = os.getenv("AZURE_OPENAI_API_VERSION")
                
                if not api_key or not endpoint or not api_version:
                    return None
                
                return AzureChatOpenAI(
                    api_key=api_key,
                    azure_endpoint=endpoint,
                    api_version=api_version,
                    azure_deployment=common_params["model"],
                    temperature=common_params["temperature"],
                    max_tokens=common_params.get("max_tokens")
                )
            
        except Exception as e:
            self.logger.error(f"Failed to create LLM for {config.provider}/{config.model_name}: {e}")
            return None
        
        return None
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their status."""
        models = []
        for config in self._available_models:
            is_available = self._is_model_available(config)
            models.append({
                "provider": config.provider,
                "model": config.model_name,
                "available": is_available,
                "api_key_env": config.api_key_env,
                "base_url_env": config.base_url_env,
            })
        return models
    
    def get_best_available_llm(self, preferred_providers: Optional[List[str]] = None) -> Optional[BaseLanguageModel]:
        """
        Get the best available LLM, optionally preferring certain providers.
        
        Args:
            preferred_providers: List of preferred providers in order of preference
        """
        if self._current_llm:
            return self._current_llm
        
        # Default preference order if none specified
        if preferred_providers is None:
            preferred_providers = [
                "openai",      # OpenAI first (most reliable)
                "azure_openai", # Azure OpenAI second (enterprise)
                "anthropic",   # Claude models
                "google",      # Gemini models
                "groq",        # Fast inference
                "mistral",     # European AI
                "custom_openai", # User's custom endpoints
                "ollama",      # Local models
                "together",    # Open source models
                "cohere",      # Canadian AI
                "fireworks"    # Fast inference platform
            ]
        
        # Try preferred providers first
        for provider in preferred_providers:
            for config in self._available_models:
                if config.provider == provider and self._is_model_available(config):
                    llm = self._create_llm_from_config(config)
                    if llm:
                        self._current_llm = llm
                        self.logger.info(f"Using LLM: {config.provider}/{config.model_name}")
                        return llm
        
        # Fallback to any available model
        for config in self._available_models:
            if self._is_model_available(config):
                llm = self._create_llm_from_config(config)
                if llm:
                    self._current_llm = llm
                    self.logger.info(f"Fallback LLM: {config.provider}/{config.model_name}")
                    return llm
        
        self.logger.error("No available LLM found!")
        return None
    
    def set_preferred_model(self, provider: str, model: str) -> bool:
        """Set a specific model as preferred."""
        for config in self._available_models:
            if config.provider == provider and config.model_name == model:
                if self._is_model_available(config):
                    llm = self._create_llm_from_config(config)
                    if llm:
                        self._current_llm = llm
                        self.logger.info(f"Set preferred LLM: {provider}/{model}")
                        return True
        return False
    
    def reset_llm(self):
        """Reset current LLM to force re-selection."""
        self._current_llm = None
    
    def get_current_model_info(self) -> Optional[Dict[str, str]]:
        """Get information about the currently selected model."""
        if not self._current_llm:
            return None
        
        # Try to extract model info from the LLM instance
        for config in self._available_models:
            try:
                test_llm = self._create_llm_from_config(config)
                if test_llm.__class__ == self._current_llm.__class__:
                    return {
                        "provider": config.provider,
                        "model": config.model_name,
                        "api_key_env": config.api_key_env
                    }
            except:
                continue
        
        return {"provider": "unknown", "model": "unknown", "api_key_env": "unknown"}


# Global LLM manager instance
llm_manager = LLMManager()
