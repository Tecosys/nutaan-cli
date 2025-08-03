"""
Configuration management for Nutaan CLI
Handles user setup wizard and persistent configuration storage
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

class ConfigManager:
    """Manages Nutaan CLI configuration and setup wizard"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".nutaan"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """Ensure the configuration directory exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                return {}
        return {}
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def has_valid_config(self) -> bool:
        """Check if user has a valid configuration"""
        config = self.load_config()
        return bool(config.get('provider') and config.get('model') and config.get('api_key'))
    
    def setup_wizard(self) -> Dict:
        """Interactive setup wizard for first-time users"""
        console.print("\n")
        console.print(Panel.fit(
            "[bold blue]🚀 Welcome to Nutaan CLI Setup Wizard[/bold blue]\n"
            "Let's configure your AI assistant!",
            border_style="blue"
        ))
        
        # Step 1: Select Provider
        provider = self._select_provider()
        
        # Step 2: Get API Configuration
        api_config = self._get_api_config(provider)
        
        # Step 3: Fetch and Select Model
        model = self._select_model(provider, api_config)
        
        # Step 4: Save Configuration
        config = {
            'provider': provider,
            'model': model,
            **api_config
        }
        
        self.save_config(config)
        
        console.print("\n")
        console.print(Panel.fit(
            f"[bold green]✅ Configuration Saved![/bold green]\n"
            f"Provider: {provider}\n"
            f"Model: {model}\n"
            f"Config saved to: {self.config_file}",
            border_style="green"
        ))
        
        return config
    
    def _select_provider(self) -> str:
        """Let user select AI provider"""
        providers = [
            ("openai", "OpenAI (GPT-4, GPT-3.5, etc.)"),
            ("anthropic", "Anthropic (Claude models)"),
            ("google", "Google (Gemini models)"),
            ("azure_openai", "Azure OpenAI"),
            ("mistral", "Mistral AI"),
            ("groq", "Groq"),
            ("together", "Together AI"),
            ("cohere", "Cohere"),
            ("fireworks", "Fireworks AI"),
            ("ollama", "Ollama (Local models)"),
            ("custom", "Custom OpenAI-compatible endpoint")
        ]
        
        console.print("\n[bold cyan]📋 Select AI Provider:[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choice", style="cyan", width=8)
        table.add_column("Provider", style="white")
        table.add_column("Description", style="dim")
        
        for i, (key, description) in enumerate(providers, 1):
            provider_name = key.replace('_', ' ').title()
            table.add_row(str(i), provider_name, description)
        
        console.print(table)
        
        while True:
            try:
                choice = int(Prompt.ask("\nEnter your choice (1-11)"))
                if 1 <= choice <= len(providers):
                    return providers[choice - 1][0]
                else:
                    console.print("[red]❌ Invalid choice. Please try again.[/red]")
            except ValueError:
                console.print("[red]❌ Please enter a valid number.[/red]")
    
    def _get_api_config(self, provider: str) -> Dict:
        """Get API configuration for the selected provider"""
        config = {}
        
        if provider == "custom":
            console.print(f"\n[bold cyan]🔧 Configure Custom OpenAI-compatible Endpoint:[/bold cyan]")
            config['base_url'] = Prompt.ask("Enter API Base URL (e.g., https://api.example.com/v1)")
            config['api_key'] = Prompt.ask("Enter API Key", password=True)
        elif provider == "azure_openai":
            console.print(f"\n[bold cyan]🔧 Configure Azure OpenAI:[/bold cyan]")
            config['azure_endpoint'] = Prompt.ask("Enter Azure OpenAI Endpoint")
            config['api_key'] = Prompt.ask("Enter API Key", password=True)
            config['api_version'] = Prompt.ask("Enter API Version", default="2024-02-01")
        elif provider == "ollama":
            console.print(f"\n[bold cyan]🔧 Configure Ollama:[/bold cyan]")
            config['base_url'] = Prompt.ask("Enter Ollama Base URL", default="http://localhost:11434")
        else:
            console.print(f"\n[bold cyan]🔧 Configure {provider.title()}:[/bold cyan]")
            config['api_key'] = Prompt.ask("Enter API Key", password=True)
        
        return config
    
    def _select_model(self, provider: str, api_config: Dict) -> str:
        """Fetch available models and let user select one"""
        console.print(f"\n[bold cyan]🤖 Fetching available models for {provider.title()}...[/bold cyan]")
        
        if provider in ["custom", "openai"]:
            return self._select_openai_model(api_config, provider)
        elif provider == "azure_openai":
            return self._select_azure_model(api_config)
        elif provider == "ollama":
            return self._select_ollama_model(api_config)
        else:
            return self._manual_model_input(provider)
    
    def _select_openai_model(self, api_config: Dict, provider: str) -> str:
        """Fetch and select OpenAI or custom OpenAI-compatible models"""
        try:
            if provider == "custom":
                base_url = api_config['base_url'].rstrip('/')
                url = f"{base_url}/models"
            else:
                url = "https://api.openai.com/v1/models"
            
            headers = {
                "Authorization": f"Bearer {api_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            with console.status("[bold green]Fetching models..."):
                response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = [model['id'] for model in data.get('data', [])]
                
                if models:
                    return self._display_model_selection(models, provider)
                else:
                    console.print("[yellow]⚠️ No models found. Please enter manually.[/yellow]")
                    return self._manual_model_input(provider)
            else:
                console.print(f"[red]❌ Failed to fetch models: {response.status_code}[/red]")
                return self._manual_model_input(provider)
                
        except Exception as e:
            console.print(f"[red]❌ Error fetching models: {str(e)}[/red]")
            return self._manual_model_input(provider)
    
    def _select_azure_model(self, api_config: Dict) -> str:
        """Select Azure OpenAI deployment model"""
        console.print("[yellow]ℹ️ For Azure OpenAI, you need to enter your deployment name.[/yellow]")
        return Prompt.ask("Enter your Azure OpenAI deployment name")
    
    def _select_ollama_model(self, api_config: Dict) -> str:
        """Fetch and select Ollama models"""
        try:
            base_url = api_config.get('base_url', 'http://localhost:11434')
            url = f"{base_url}/api/tags"
            
            with console.status("[bold green]Fetching Ollama models..."):
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                
                if models:
                    return self._display_model_selection(models, "ollama")
                else:
                    console.print("[yellow]⚠️ No models found. Please enter manually.[/yellow]")
                    return self._manual_model_input("ollama")
            else:
                console.print(f"[red]❌ Failed to fetch models: {response.status_code}[/red]")
                return self._manual_model_input("ollama")
                
        except Exception as e:
            console.print(f"[red]❌ Error fetching models: {str(e)}[/red]")
            return self._manual_model_input("ollama")
    
    def _display_model_selection(self, models: List[str], provider: str) -> str:
        """Display models in a table and let user select"""
        console.print(f"\n[bold cyan]📋 Available models for {provider.title()}:[/bold cyan]")
        
        # Group models for better display
        chat_models = [m for m in models if any(x in m.lower() for x in ['gpt', 'claude', 'gemini', 'llama', 'mistral', 'chat'])]
        other_models = [m for m in models if m not in chat_models]
        
        # Prioritize chat models
        display_models = chat_models + other_models
        
        # Limit to first 20 models for better UX
        if len(display_models) > 20:
            display_models = display_models[:20]
            console.print(f"[dim]Showing first 20 models out of {len(models)} available...[/dim]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choice", style="cyan", width=8)
        table.add_column("Model ID", style="white")
        
        for i, model in enumerate(display_models, 1):
            table.add_row(str(i), model)
        
        console.print(table)
        
        # Add option to enter manually
        console.print(f"\n[dim]Enter {len(display_models) + 1} to input model name manually[/dim]")
        
        while True:
            try:
                choice = int(Prompt.ask(f"\nEnter your choice (1-{len(display_models) + 1})"))
                if 1 <= choice <= len(display_models):
                    return display_models[choice - 1]
                elif choice == len(display_models) + 1:
                    return self._manual_model_input(provider)
                else:
                    console.print("[red]❌ Invalid choice. Please try again.[/red]")
            except ValueError:
                console.print("[red]❌ Please enter a valid number.[/red]")
    
    def _manual_model_input(self, provider: str) -> str:
        """Manual model input when auto-fetch fails"""
        console.print(f"\n[bold cyan]✏️ Enter model name for {provider.title()}:[/bold cyan]")
        
        # Provide suggestions based on provider
        suggestions = {
            'openai': 'gpt-4o, gpt-4o-mini, gpt-3.5-turbo',
            'anthropic': 'claude-3-5-sonnet-20241022, claude-3-haiku-20240307',
            'google': 'gemini-2.0-flash-exp, gemini-1.5-pro',
            'azure_openai': 'your-deployment-name',
            'mistral': 'mistral-large-latest, mistral-small-latest',
            'groq': 'llama-3.1-70b-versatile, mixtral-8x7b-32768',
            'custom': 'depends on your endpoint',
            'ollama': 'llama2, codellama, mistral'
        }
        
        if provider in suggestions:
            console.print(f"[dim]Common models: {suggestions[provider]}[/dim]")
        
        return Prompt.ask("Model name")
    
    def get_env_config(self) -> Dict:
        """Convert saved config to environment variables format"""
        config = self.load_config()
        if not config:
            return {}
        
        provider = config.get('provider')
        env_config = {}
        
        if provider == 'openai':
            env_config['OPENAI_API_KEY'] = config.get('api_key')
            env_config['OPENAI_MODELS'] = config.get('model')
        elif provider == 'anthropic':
            env_config['ANTHROPIC_API_KEY'] = config.get('api_key')
            env_config['ANTHROPIC_MODELS'] = config.get('model')
        elif provider == 'google':
            env_config['GOOGLE_API_KEY'] = config.get('api_key')
            env_config['GOOGLE_MODELS'] = config.get('model')
        elif provider == 'azure_openai':
            env_config['AZURE_OPENAI_API_KEY'] = config.get('api_key')
            env_config['AZURE_OPENAI_ENDPOINT'] = config.get('azure_endpoint')
            env_config['AZURE_OPENAI_API_VERSION'] = config.get('api_version', '2024-02-01')
            env_config['AZURE_OPENAI_MODELS'] = config.get('model')
        elif provider == 'mistral':
            env_config['MISTRAL_API_KEY'] = config.get('api_key')
            env_config['MISTRAL_MODELS'] = config.get('model')
        elif provider == 'groq':
            env_config['GROQ_API_KEY'] = config.get('api_key')
            env_config['GROQ_MODELS'] = config.get('model')
        elif provider == 'together':
            env_config['TOGETHER_API_KEY'] = config.get('api_key')
            env_config['TOGETHER_MODELS'] = config.get('model')
        elif provider == 'cohere':
            env_config['COHERE_API_KEY'] = config.get('api_key')
            env_config['COHERE_MODELS'] = config.get('model')
        elif provider == 'fireworks':
            env_config['FIREWORKS_API_KEY'] = config.get('api_key')
            env_config['FIREWORKS_MODELS'] = config.get('model')
        elif provider == 'ollama':
            env_config['OLLAMA_BASE_URL'] = config.get('base_url', 'http://localhost:11434')
            env_config['OLLAMA_MODELS'] = config.get('model')
        elif provider == 'custom':
            env_config['CUSTOM_API_KEY'] = config.get('api_key')
            env_config['CUSTOM_BASE_URL'] = config.get('base_url')
            env_config['CUSTOM_MODELS'] = config.get('model')
        
        # Set active providers
        env_config['PROVIDERS'] = provider.replace('_', '')
        
        return env_config
