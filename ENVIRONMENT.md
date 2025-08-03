# Environment Configuration Guide

Nutaan CLI supports flexible environment configuration for different deployment scenarios.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your API keys in `.env`:**
   ```bash
   # Add your API keys
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   # ... etc
   ```

3. **Run Nutaan:**
   ```bash
   nutaan  # Uses .env automatically
   ```

## Environment File Options

### Using Custom Environment Files

```bash
# Load specific environment file
nutaan -e .env.production
nutaan -e config/development.env
nutaan --env team-config/.env
```

### Pre-configured Environment Templates

#### 🏭 **Production** (`.env.production`)
- High-performance models (GPT-4, Claude)
- Production endpoints
- Full feature set

```bash
nutaan -e .env.production
```

#### 🛠️ **Development** (`.env.development`)  
- Cost-effective models (Groq, Together)
- Development endpoints
- Fast iteration

```bash
nutaan -e .env.development
```

#### 💻 **Local** (`.env.local`)
- Offline-first with Ollama
- No API keys required
- Privacy-focused

```bash
nutaan -e .env.local
```

## Environment Variables

### AI Model Providers
```bash
# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key

# Google
GOOGLE_API_KEY=your_google_key

# Groq (Fast inference)
GROQ_API_KEY=your_groq_key

# Local Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Custom endpoints
CUSTOM_API_KEY=your_custom_key
CUSTOM_BASE_URL=https://your-endpoint.com/
```

### Search & Tools
```bash
# Web search
BRAVE_SEARCH_API_KEY=your_brave_key
```

## Model Management

```bash
# List available models with current environment
nutaan --list-models

# Set preferred model
nutaan --set-model openai gpt-4o

# Check current model
nutaan --current-model

# Reset to auto-selection
nutaan --reset-model
```

## Environment File Priority

1. **Command-line specified:** `-e custom.env`
2. **Default `.env`** in current directory
3. **Environment variables** already set in shell
4. **Built-in defaults**

## Examples

### Team Development Setup
```bash
# Create team environment
cat > .env.team << EOF
# Team shared development environment
GROQ_API_KEY=team_groq_key_here
CUSTOM_API_KEY=team_custom_key
CUSTOM_BASE_URL=https://team-ai-endpoint.com/
EOF

# Use team environment
nutaan -e .env.team
```

### CI/CD Pipeline
```bash
# In your CI/CD pipeline
export OPENAI_API_KEY=$CI_OPENAI_KEY
nutaan --test  # Uses environment variables
```

### Multi-Project Setup
```bash
# Project A
nutaan -e projects/projectA/.env

# Project B  
nutaan -e projects/projectB/.env
```

## Best Practices

1. **Never commit real API keys** to version control
2. **Use different environments** for different purposes
3. **Keep `.env.example`** updated with latest variables
4. **Use environment-specific models** to optimize costs
5. **Test locally** with Ollama before using paid APIs

## Troubleshooting

### No models available
```bash
# Check environment loading
nutaan -e .env.development --list-models

# Verify API keys are set
nutaan --model-status
```

### Environment not loading
```bash
# Check file exists
ls -la .env*

# Manually test loading
nutaan -e .env.development --current-model
```

### Model access issues
```bash
# Reset model selection
nutaan --reset-model

# List available models
nutaan --list-models

# Check specific environment
nutaan -e .env.production --model-status
```
