# Nutaan CLI - Your AI Developer Assistant in the Terminal 🚀

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/Tecosys/nutaan-cli)

**Nutaan-CLI** is a powerful ReAct (Reasoning and Acting) Python assistant with AI capabilities, featuring Claude CLI-style tool displays, persistent task management, and professional terminal UI.

*Made by Tecosys*

## ✨ Features

- 🤖 **AI-Powered Assistant** - Advanced reasoning with LangGraph and OpenAI
- 📋 **Plan Management** - Create, track, and complete tasks with strikethrough formatting
- 🔧 **Multiple Tools** - Web search, file operations, bash commands, and more
- 💭 **Think Mode** - Enhanced reasoning for complex problems
- 🎨 **Rich Terminal UI** - Beautiful formatting with colors and progress tracking
- 💾 **Persistent Storage** - Plans and session history automatically saved
- 🚀 **Multiple Run Methods** - CLI command or Python module execution

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install nutaan-cli
```

### From Source (Development)
```bash
git clone https://github.com/Tecosys/nutaan-cli.git
cd nutaan-cli
pip install -e .
```

## 🚀 Quick Start

### Basic Usage
```bash
# Interactive mode
nutaan

# Single prompt
nutaan "Hello, how can you help me?"

# Think mode for complex reasoning
nutaan --think "Analyze this complex problem"

# Show help
nutaan --help

# Check version
nutaan --version
```

### Python Module Execution
```bash
# All commands work with module execution too
python3 -m nutaan
python3 -m nutaan "Hello world"
python3 -m nutaan --think "Complex reasoning task"
```

## 📋 Plan Management

Nutaan-CLI includes a powerful plan tool for organizing and tracking tasks with visual progress indicators.

### Creating Plans
```bash
# Create a plan with multiple tasks
nutaan "Create a plan for building a website with tasks: Setup HTML, Add CSS, JavaScript functionality, Testing, Deployment"
```

**Output:**
```
• Website Project
Build a responsive website

  ☐ Setup HTML structure
  ☐ Add CSS styling  
  ☐ JavaScript functionality
  ☐ Testing across browsers
  ☐ Deployment

Progress: 0/5 items completed (0.0%)
```

### Managing Tasks
```bash
# Complete a task (adds strikethrough)
nutaan "Complete the HTML setup task"

# Add new tasks
nutaan "Add a new task: Add responsive design"

# View all plans
nutaan "List all my plans"

# Show specific plan
nutaan "Show me the website project plan"
```

**Completed tasks show with strikethrough:**
```
• Website Project
Build a responsive website

  ☑ Setup HTML structure        # ✅ Completed with strikethrough
  ☐ Add CSS styling
  ☐ JavaScript functionality
  ☐ Testing across browsers
  ☐ Deployment

Progress: 1/5 items completed (20.0%)
```

### Plan Tool Commands
```bash
# Direct plan tool usage
nutaan "Use plan tool to: create plan \"Project Name\" \"Description\" [\"Task 1\", \"Task 2\"]"
nutaan "Use plan tool to: complete item plan_id item_id"
nutaan "Use plan tool to: add item plan_id \"New task\""
nutaan "Use plan tool to: list plans"
```

## 🛠️ Available Tools

### Core Tools
- **🧠 Think Tool** - Advanced reasoning and problem analysis
- **📋 Plan Tool** - Task management with progress tracking
- **🔍 Web Search** - Real-time information retrieval with Brave Search
- **📁 File Operations** - Read, write, and edit files with permission system
- **💻 Bash Commands** - Execute system commands safely
- **✏️ File Editing** - Smart file editing with diff previews

### Tool Examples
```bash
# Web search
nutaan "Search for latest Python best practices"

# File operations
nutaan "Read the config.json file and explain its structure"
nutaan "Create a new Python script for data processing"

# System commands
nutaan "Check disk usage and system status"

# Complex reasoning
nutaan --think "Analyze the pros and cons of different deployment strategies"
```

## 📊 Session Management

### History & Statistics
```bash
# View session history
nutaan --history

# Show usage statistics
nutaan --stats

# Resume previous conversation
nutaan "Resume our last conversation about the website project"
```

### Data Storage
- **Plans:** `.nutaan_data/plans.json` - All task plans and progress
- **Sessions:** Stored in memory during runtime
- **Configuration:** Automatic environment detection

## 🎯 Usage Examples

### Development Workflow
```bash
# 1. Create project plan
nutaan "Create a plan for building a Python web scraper with tasks: Setup environment, Design data model, Implement scraper, Add error handling, Write tests, Documentation"

# 2. Work through tasks
nutaan "Complete the environment setup task"
nutaan "Help me implement the data model for the scraper"

# 3. Track progress
nutaan "Show my scraper project progress"
```

### Learning & Research
```bash
# Complex analysis with think mode
nutaan --think "Explain the differences between async/await and threading in Python, with practical examples"

# Research with web search
nutaan "Find the latest best practices for FastAPI development"

# Create learning plan
nutaan "Create a learning plan for mastering React with tasks: JSX basics, Components, State management, Hooks, Routing, Testing"
```

### System Administration
```bash
# System monitoring
nutaan "Check system resources and suggest optimizations"

# File management
nutaan "Organize the Downloads folder by file type"

# Documentation
nutaan "Create documentation for this Python project based on the code structure"
```

## ⚙️ Configuration

### Using Nutaan API (Recommended)

For the best experience, use the official Nutaan API:

1. **Get API Key**: Visit [nutaan.com](https://nutaan.com) and create an API key in Settings
2. **Create Environment File**: Create a `.env` file with your configuration:

```bash
# LiteLLM Proxy Configuration
CUSTOM_API_KEY=nut-xxxxxxxxxxxxxxxx
CUSTOM_BASE_URL=https://api-prod.nutaan.com
CUSTOM_MODELS=nutaan

# Enable custom provider
PROVIDERS=custom
```

3. **Run with Environment**: Use the `-e` flag to specify your environment file:

```bash
nutaan -e .env "Your query here"
```

### Alternative: OpenAI API
```bash
# Optional: Custom API endpoints
export OPENAI_API_BASE="https://your-api-endpoint.com/"
export OPENAI_API_KEY="your-api-key"
```

### Command Line Options
```bash
nutaan --help                    # Show all options
nutaan --think                   # Enable think mode
nutaan --test                    # Run test queries
nutaan --history                 # Manage session history
nutaan --stats                   # Show usage statistics
nutaan --version                 # Show version info
```

## 🎨 Rich Terminal UI

Nutaan-CLI provides a beautiful terminal experience with:

- **🎨 Syntax highlighting** for code and diffs
- **📊 Progress bars** for task completion
- **✅ Strikethrough formatting** for completed tasks
- **🔧 Claude CLI-style** tool call displays
- **📱 Responsive layout** that adapts to terminal size

## 🏗️ Architecture

### Package Structure
```
nutaan/
├── __init__.py              # Package initialization
├── __main__.py              # Module execution entry point
├── cli.py                   # Command-line interface
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── agent_manager.py     # Agent creation and management
│   ├── session_history.py  # Session persistence
│   └── prompt_system.py    # System prompts and plan integration
└── tools/                   # Available tools
    ├── __init__.py
    ├── plan_tool.py         # Task management with Rich UI
    ├── brave_search_tool.py # Web search functionality
    ├── file_read_tool.py    # File reading operations
    ├── file_write_tool.py   # File writing with previews
    ├── file_edit_tool.py    # File editing with diffs
    ├── bash_run_tool.py     # System command execution
    └── think_tool.py        # Advanced reasoning
```

### Data Storage
```
.nutaan_data/
└── plans.json               # Persistent plan storage
```

### Technology Stack
- **LangGraph 0.6.2** - Agent orchestration and state management
- **LangChain** - LLM integration and tool management  
- **Rich 14.1.0** - Beautiful terminal UI with formatting
- **Pydantic** - Data validation and settings
- **OpenAI/Compatible APIs** - Language model inference

## 🧪 Development

### Setting Up Development Environment
```bash
# Clone repository
git clone https://github.com/Tecosys/nutaan-cli.git
cd nutaan-cli

# Install in development mode
pip install -e .

# Run tests
python -m pytest

# Run with development logging
nutaan --debug "Test message"
```

### Adding New Tools
1. Create tool class in `nutaan/tools/` following the pattern:
```python
from langchain.tools import BaseTool
from pydantic import Field

class MyCustomTool(BaseTool):
    name: str = "my_custom_tool"
    description: str = "Description of what the tool does"
    
    def _run(self, query: str) -> str:
        # Tool implementation
        return result
```

2. Add to `nutaan/tools/__init__.py`:
```python
from .my_custom_tool import MyCustomTool
__all__ = [..., "MyCustomTool"]
```

3. Import in `nutaan/core/agent_manager.py` and add to tools list

### Extending Plan Tool
The plan tool supports rich formatting and persistence:
```python
# Custom plan actions
plan_manager = PlanManager()
plan_id = plan_manager.create_plan("My Plan", "Description", ["Task 1", "Task 2"])
plan_manager.complete_item(plan_id, "item_1")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for public methods
- Add tests for new functionality
- Update documentation for new features

## 🐛 Troubleshooting

### Common Issues

#### Installation Problems
```bash
# If pip install fails, try upgrading pip
pip install --upgrade pip
pip install -e .
```

#### Missing API Keys
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Verify configuration
nutaan "Test API connection"
```

#### Permission Errors
```bash
# Check file permissions
ls -la ~/.nutaan_data/

# Reset permissions if needed
chmod 755 ~/.nutaan_data/
chmod 644 ~/.nutaan_data/plans.json
```

### Debug Mode
```bash
# Enable debug logging
nutaan --debug "Your query here"

# View detailed error information
nutaan --verbose "Your query here"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangGraph](https://langraph-doc.vercel.app/)
- UI powered by [Rich](https://rich.readthedocs.io/)
- Inspired by [Claude CLI](https://github.com/anthropics/claude-cli)
- Task management inspired by modern todo applications

## 📞 Support

- 🌐 Visit: [tecosys.in](https://tecosys.in) | [nutaan.com](https://nutaan.com)
- 📧 Email: info@tecosys.in
- 🐛 Issues: [GitHub Issues](https://github.com/Tecosys/nutaan-cli/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Tecosys/nutaan-cli/discussions)
- 📖 Documentation: [Wiki](https://github.com/Tecosys/nutaan-cli/wiki)

## 🚀 Roadmap

### Upcoming Features
- 📱 **Mobile companion app** - Control Nutaan from your phone
- 🔌 **Plugin system** - Community-driven tool ecosystem
- 🌐 **Web interface** - Browser-based interaction
- 📊 **Analytics dashboard** - Usage insights and productivity metrics
- 🤝 **Team collaboration** - Shared plans and project management
- 🔄 **CI/CD integration** - Automated workflows and deployments

### Version History
- **v1.0.0** - Initial release with plan tool and Rich UI
- **v0.9.0** - Claude CLI-style tool displays
- **v0.8.0** - Package structure and pip distribution
- **v0.7.0** - Think mode and advanced reasoning

---

**Made with ❤️ by Tecosys** | [Explore tecosys.in](https://tecosys.in) | [Visit nutaan.com](https://nutaan.com)

*Empowering developers with AI-assisted productivity*
