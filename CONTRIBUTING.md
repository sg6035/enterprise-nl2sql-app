# Contributing to Enterprise NL2SQL Service with Ollama

## 🔄 Git Workflow Guide

### Branching Strategy

We use **Git Flow** branching strategy:

- `main` - Production-ready code with Ollama integration
- `develop` - Integration branch for features
- `feature/*` - New features (model optimization, prompt engineering, etc.)
- `hotfix/*` - Critical bug fixes
- `release/*` - Release preparation

### Branch Naming Convention

```
feature/add-schema-caching
feature/implement-user-auth
feature/optimize-phi3-prompts
feature/add-model-switching
hotfix/fix-ollama-connection
release/v1.2.0
bugfix/resolve-inference-timeout
improvement/optimize-model-performance
```

## 🚀 Development Setup

### 1. Prerequisites
```bash
# Install Docker and Docker Compose
sudo apt update
sudo apt install docker.io docker-compose git
sudo usermod -aG docker $USER

# Install Ollama for local development
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Download required models
ollama pull phi3:3.8b
ollama pull phi3:mini      # For faster testing
```

### 2. Initialize Repository
```bash
cd /Users/theseus/allai/nl2sql/enterprise-nl2sql
git init
git add .
git commit -m "Initial commit: Enterprise NL2SQL Service with Ollama"
```

### 3. Local Development Environment
```bash
# Create development environment file
cp .env.example .env.dev

# Configure for local Ollama
cat >> .env.dev << EOF
ENVIRONMENT=development
DEBUG=true
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=phi3:mini
OLLAMA_MODEL=phi3:mini
API_KEY=test-api-key
LOG_LEVEL=DEBUG
EOF

# Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 4. Create GitHub Repository
```bash
# Replace 'your-username' with your GitHub username
gh repo create enterprise-nl2sql-ollama --public --description "Enterprise NL2SQL service with local Ollama LLMs"

# Or create manually at https://github.com/new
```

### 5. Connect to Remote
```bash
git remote add origin https://github.com/your-username/enterprise-nl2sql-ollama.git
git branch -M main
git push -u origin main
```

## 📋 Daily Workflow

### Starting New Feature
```bash
# Switch to develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Work on your feature...
# ... make changes ...

# Stage and commit changes
git add .
git commit -m "feat: add new feature description"

# Push feature branch
git push -u origin feature/your-feature-name
```

### Creating Pull Request
```bash
# Push your feature branch
git push origin feature/your-feature-name

# Create PR using GitHub CLI (optional)
gh pr create --title "Add new feature" --body "Description of changes"

# Or create manually on GitHub
```

### Merging and Cleanup
```bash
# After PR is merged, cleanup
git checkout develop
git pull origin develop
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## 🧪 Development & Testing

### Local Development Workflow
```bash
# Start Ollama (required for development)
ollama serve &

# Verify models are available
ollama list

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests with local Ollama
pytest tests/ -v

# Test specific model
LLM_MODEL=phi3:mini pytest tests/test_nl2sql_service.py

# Monitor inference times during development
docker-compose logs -f nl2sql-api | grep inference_time
```

### Model Testing
```bash
# Test different models locally
ollama pull phi3:mini
ollama pull phi3:3.8b
ollama pull llama3.1:8b

# Switch models for testing
export LLM_MODEL=phi3:mini
export OLLAMA_MODEL=phi3:mini
docker-compose restart nl2sql-api

# Benchmark inference times
time curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer test-api-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many users?", "database_url": "..."}'
```

### Prompt Engineering Testing
```bash
# Test prompt variations
# Edit app/services/nl2sql_service.py
# Restart service and test
docker-compose restart nl2sql-api

# Test with various question types
curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer test-api-key" \
  -d '{"question": "Count all users"}'

curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer test-api-key" \
  -d '{"question": "How many rows in users table?"}'
```

## 🔧 Useful Git Commands

### Branch Management
```bash
# List all branches
git branch -a

# Create and switch to new branch
git checkout -b new-branch-name

# Switch between branches
git checkout branch-name

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name
```

### Committing Best Practices
```bash
# Stage specific files
git add file1.py file2.py

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "type: brief description"

# Amend last commit
git commit --amend -m "new message"
```

### Syncing with Remote
```bash
# Fetch latest changes
git fetch origin

# Pull latest changes
git pull origin branch-name

# Push changes
git push origin branch-name

# Force push (use carefully)
git push --force-with-lease origin branch-name
```

## 📝 Commit Message Convention

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

### Types:
- `feat` - New feature (model integration, prompt optimization)
- `fix` - Bug fix (inference issues, connection problems)
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring (prompt engineering, model switching)
- `test` - Adding or updating tests
- `chore` - Maintenance tasks (model updates, dependency updates)

### Examples:
```
feat(ollama): add support for CodeLlama model
feat(prompts): optimize Phi-3 prompt templates for better SQL generation
fix(inference): resolve timeout issues with large schema
fix(docker): fix Ollama connectivity in containerized environment
docs(readme): update Ollama installation instructions
refactor(service): improve model switching logic
test(phi3): add unit tests for Phi-3 specific features
chore(models): update Phi-3 to latest version
```

## 🔄 Advanced Git Operations

### Stashing Changes
```bash
# Save current work temporarily
git stash

# List stashes
git stash list

# Apply most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{0}

# Create named stash
git stash save "work in progress on feature X"
```

### Cherry Picking
```bash
# Apply specific commit to current branch
git cherry-pick commit-hash

# Cherry pick multiple commits
git cherry-pick commit1 commit2 commit3
```

### Interactive Rebase
```bash
# Rebase last 3 commits interactively
git rebase -i HEAD~3

# Rebase against develop branch
git rebase -i develop
```

### Resolving Conflicts
```bash
# When conflicts occur during merge/rebase
git status

# Edit conflicted files
# Remove conflict markers and choose correct version

# Mark as resolved
git add conflicted-file.py

# Continue rebase/merge
git rebase --continue
# or
git merge --continue
```

## 🏷️ Tagging and Releases

### Creating Tags
```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Create lightweight tag
git tag v1.0.0

# Push tags to remote
git push origin --tags

# Push specific tag
git push origin v1.0.0
```

### Release Workflow
```bash
# Create release branch
git checkout develop
git checkout -b release/v1.1.0

# Update version numbers, changelog, etc.
# ... make release preparations ...

# Commit release changes
git commit -m "chore: prepare release v1.1.0"

# Merge to main
git checkout main
git merge --no-ff release/v1.1.0

# Tag the release
git tag -a v1.1.0 -m "Release version 1.1.0"

# Merge back to develop
git checkout develop
git merge --no-ff release/v1.1.0

# Push everything
git push origin main develop --tags

# Delete release branch
git branch -d release/v1.1.0
```

## 🛠️ IDE Integration (VS Code)

### Recommended Extensions
- GitLens
- Git History
- Git Graph
- GitHub Pull Requests
- Git Blame

### VS Code Git Commands
- `Cmd+Shift+P` → Git commands
- `Cmd+Shift+G` → Source Control panel
- `Cmd+K Cmd+C` → Commit changes
- `Cmd+K Cmd+P` → Push changes

## 📊 Repository Structure for Ollama Integration

```
enterprise-nl2sql/
├── .github/                    # GitHub workflows and templates
│   ├── workflows/
│   │   ├── ci.yml             # CI/CD with Ollama testing
│   │   ├── deploy.yml         # Deployment with model management
│   │   └── model-tests.yml    # Model-specific testing
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── app/                       # Application code
│   ├── services/
│   │   ├── nl2sql_service.py  # Main service with Ollama integration
│   │   └── ollama_service.py  # Ollama client wrapper
│   ├── core/
│   │   ├── security.py        # Updated JWT handling
│   │   └── config.py          # Ollama configuration
├── models/                    # Model configurations and prompts
│   ├── phi3/                  # Phi-3 specific configurations
│   ├── llama/                 # Llama model configurations
│   └── prompts/               # Prompt templates
├── tests/                     # Test files with Ollama integration
├── docs/                      # Updated documentation
├── scripts/                   # Model management scripts
├── .env.example              # Environment template with Ollama
├── docker-compose.yml        # Updated for Ollama connectivity
├── docker-compose.dev.yml    # Development environment
├── CONTRIBUTING.md           # This file
├── CHANGELOG.md              # Updated with Ollama integration
└── README.md                 # Updated setup instructions
```

## 🔐 Security Considerations

### Protecting Secrets
```bash
# Never commit these files:
.env
config/secrets.yml
ssl-certs/
private-keys/

# Use environment variables or secret management
git secret init
git secret add .env
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📈 Monitoring Repository

### GitHub Analytics
- Insights → Contributors
- Insights → Traffic
- Insights → Community
- Security → Dependency graph

### Useful Aliases
```bash
# Add to ~/.gitconfig
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    ca = commit -a
    ps = push
    pl = pull
    lg = log --oneline --graph --decorate --all
    last = log -1 HEAD
    unstage = reset HEAD --
```

## 🚀 Automation

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test
        run: pytest
```

This guide provides everything you need for effective Git workflow with your Enterprise NL2SQL project!




I'll help you create a Git repository for your Enterprise NL2SQL project and provide a comprehensive guide for Git workflow. Let me first check the current requirements.txt file and then set up the Git repository. Great! Now let me help you set up a Git repository for your Enterprise NL2SQL project. I'll create the necessary Git configuration files and provide you with a comprehensive workflow guide. 

Made changes.

Made changes.

Summarized conversation historyNow let me run the Git initialization commands to set up your repository: Perfect! Now let me create a basic GitHub Actions workflow for CI/CD: 

Made changes.

Made changes.

Made changes.

Now let me check the current git status and show you how to create the GitHub repository: ## 🎉 Your Enterprise NL2SQL Repository is Ready!

### 📋 Quick Setup Summary

✅ **Git Repository Initialized** - Your project is now version controlled  
✅ **Professional Branching Strategy** - Git Flow workflow ready  
✅ **CI/CD Pipeline** - GitHub Actions configured  
✅ **Documentation Complete** - README, Contributing guide, Changelog  
✅ **Security & Quality** - Pre-commit hooks and scanning ready  

### 🚀 Next Steps to Create GitHub Repository

#### Option 1: Using GitHub CLI (Recommended)
```bash
# Install GitHub CLI if not already installed
brew install gh

# Authenticate with GitHub
gh auth login

# Create repository and push
cd /Users/theseus/allai/nl2sql/enterprise-nl2sql
gh repo create enterprise-nl2sql --public --description "Enterprise-grade NL2SQL service with LLMs and advanced ML features"
git remote add origin https://github.com/YOUR_USERNAME/enterprise-nl2sql.git
git push -u origin main
```

#### Option 2: Manual GitHub Creation
1. Go to [https://github.com/new](https://github.com/new)
2. Repository name: enterprise-nl2sql
3. Description: `Enterprise-grade NL2SQL service with LLMs and advanced ML features`
4. Choose Public/Private
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

Then connect your local repo:
```bash
cd /Users/theseus/allai/nl2sql/enterprise-nl2sql
git remote add origin https://github.com/YOUR_USERNAME/enterprise-nl2sql.git
git push -u origin main
```

### 🔄 Daily Development Workflow

#### 1. Starting a New Feature
```bash
# Create and switch to develop branch
git checkout -b develop
git push -u origin develop

# Create feature branch
git checkout -b feature/add-query-optimization
```

#### 2. Working on Features
```bash
# Make your changes...
git add .
git commit -m "feat(query): add caching optimization for repeated queries"
git push origin feature/add-query-optimization
```

#### 3. Creating Pull Requests
```bash
# Using GitHub CLI
gh pr create --title "Add query optimization" --body "Implements Redis caching for repeated queries"

# Or create manually on GitHub web interface
```

#### 4. Merging and Cleanup
```bash
# After PR is merged
git checkout develop
git pull origin develop
git branch -d feature/add-query-optimization
```

### 🛠️ Repository Features Included

#### **GitHub Actions CI/CD**
- ✅ Automated testing with PostgreSQL/Redis
- ✅ Security scanning with Bandit
- ✅ Docker builds and pushes
- ✅ Code coverage reporting
- ✅ Multi-platform builds (AMD64/ARM64)

#### **Development Tools**
- ✅ Pull request templates
- ✅ Issue templates (can be added)
- ✅ Comprehensive `.gitignore`
- ✅ Semantic commit conventions
- ✅ Changelog automation ready

#### **Documentation**
- ✅ `README.md` - Project overview and setup
- ✅ `CONTRIBUTING.md` - Git workflow guide
- ✅ `USAGE.md` - API usage examples
- ✅ `CHANGELOG.md` - Version history

### 🔧 Required GitHub Secrets

For CI/CD to work properly, add these secrets in GitHub Settings → Secrets:

```bash
OPENAI_API_KEY          # Your OpenAI API key
DOCKERHUB_USERNAME      # Docker Hub username
DOCKERHUB_TOKEN         # Docker Hub access token
```

### 📊 Repository Structure Overview

```
enterprise-nl2sql/
├── .github/                 # GitHub templates and workflows
│   ├── workflows/ci.yml     # CI/CD pipeline
│   └── PULL_REQUEST_TEMPLATE.md
├── app/                     # Main application code
├── scripts/                 # Database and deployment scripts  
├── .gitignore              # Git ignore rules
├── CONTRIBUTING.md         # Development workflow guide
├── CHANGELOG.md            # Version history
├── README.md               # Project documentation
├── docker-compose.yml      # Multi-service orchestration
└── requirements.txt        # Python dependencies
```

### 🎯 What You Can Do Now

1. **Push to GitHub** using the commands above
2. **Invite collaborators** to your repository
3. **Set up protected branches** (main/develop)
4. **Configure branch protection rules**
5. **Add issue templates** for bug reports and features
6. **Set up project boards** for task management

### 🔄 Branching Strategy Quick Reference

- `main` → Production releases
- `develop` → Integration branch  
- `feature/*` → New features
- `hotfix/*` → Critical fixes
- `release/*` → Release preparation

Your enterprise NL2SQL service is now ready for professional development with a complete Git workflow, CI/CD pipeline, and production deployment capabilities! 🚀

Would you like me to help you with any specific aspect of the repository setup or development workflow?