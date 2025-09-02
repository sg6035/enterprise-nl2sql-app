# Contributing to Enterprise NL2SQL Service

## 🔄 Git Workflow Guide

### Branching Strategy

We use **Git Flow** branching strategy:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `hotfix/*` - Critical bug fixes
- `release/*` - Release preparation

### Branch Naming Convention

```
feature/add-schema-caching
feature/implement-user-auth
hotfix/fix-sql-injection
release/v1.2.0
bugfix/resolve-connection-timeout
improvement/optimize-query-performance
```

## 🚀 Quick Setup

### 1. Initialize Repository
```bash
cd /Users/theseus/allai/nl2sql/enterprise-nl2sql
git init
git add .
git commit -m "Initial commit: Enterprise NL2SQL Service"
```

### 2. Create GitHub Repository
```bash
# Replace 'your-username' with your GitHub username
gh repo create enterprise-nl2sql --public --description "Enterprise-grade NL2SQL service with LLMs"

# Or create manually at https://github.com/new
```

### 3. Connect to Remote
```bash
git remote add origin https://github.com/your-username/enterprise-nl2sql.git
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
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

### Examples:
```
feat(api): add user authentication endpoints
fix(database): resolve connection timeout issue
docs(readme): update deployment instructions
refactor(service): optimize query processing logic
test(auth): add unit tests for login functionality
chore(deps): update OpenAI client to latest version
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

## 📊 Repository Structure

```
enterprise-nl2sql/
├── .github/                    # GitHub workflows and templates
│   ├── workflows/
│   │   ├── ci.yml             # Continuous Integration
│   │   ├── deploy.yml         # Deployment workflow
│   │   └── security.yml       # Security scanning
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── app/                       # Application code
├── tests/                     # Test files
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
├── .gitignore                 # Git ignore rules
├── .gitattributes            # Git attributes
├── CONTRIBUTING.md           # This file
├── CHANGELOG.md              # Version history
└── README.md                 # Project documentation
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
