# Contributing to Azure Autonomous Newsroom

Thank you for your interest in contributing to the Azure Autonomous Newsroom (AAN) project! This document provides guidelines and instructions for contributing.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Report issues responsibly
- No harassment or discrimination

## 📋 Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/your-org/newsroom.git
cd newsroom
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming convention:
- `feature/description` — New features
- `fix/description` — Bug fixes
- `docs/description` — Documentation updates
- `infra/description` — Infrastructure changes
- `refactor/description` — Code refactoring

### 3. Set Up Development Environment

**For Python Agent Development:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r agents/requirements.txt
pip install -r agents/requirements-dev.txt
```

**For Infrastructure (Terraform):**
```bash
cd infrastructure
terraform init
terraform plan
```

## 💻 Development Guidelines

### Python Code Style
- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Maximum line length: 100 characters
- Format with `black`: `black agents/`
- Lint with `pylint`: `pylint agents/`
- Type check with `mypy`: `mypy agents/`

### Testing Requirements
- Write unit tests for new features
- Achieve ≥80% code coverage
- Run tests before committing:
  ```bash
  pytest agents/tests/ -v --cov=agents
  ```

### Infrastructure Code
- Validate Terraform:
  ```bash
  terraform -chdir=infrastructure fmt -recursive
  terraform -chdir=infrastructure validate
  terraform -chdir=infrastructure plan
  ```
- Use meaningful resource names
- Include tags for cost tracking
- Document outputs and variables

### Documentation
- Update [SYSTEM_DESIGN_v3.0.md](/docs/SYSTEM_DESIGN_v3.0.md) for architecture changes
- Update [IMPLEMENTATION_ROADMAP.md](/docs/IMPLEMENTATION_ROADMAP.md) for timeline changes
- Add docstrings to all functions/classes
- Update README if adding dependencies
- Validate markdown links: `npm run check-links`

## 🔄 Pull Request Process

1. **Before submitting:**
   - Run all tests: `pytest agents/tests/`
   - Run linting: `black agents/`, `pylint agents/`
   - Validate Terraform: `terraform validate`
   - Check documentation links

2. **Submit PR:**
   - Use the PR template (auto-populated)
   - Reference related issues: `Closes #123`
   - Provide clear description of changes
   - Include test results screenshot if applicable

3. **Code Review:**
   - Respond to review comments promptly
   - Make requested changes in new commits (don't rebase)
   - Request re-review after changes

4. **Merge Criteria:**
   - ✅ CI/CD pipeline passes
   - ✅ At least one approval from maintainers
   - ✅ No merge conflicts
   - ✅ All conversations resolved

## 📝 Commit Message Format

```
[PHASE-X] Brief description (50 chars max)

Detailed explanation (if needed):
- Bullet point 1
- Bullet point 2

Fixes #123
```

Examples:
```
[PHASE-0] Add Foundry SDK initialization to base agent
[PHASE-1] Fix Scout agent vision prompt parsing
[INFRA] Update Cosmos DB throughput settings
[DOCS] Add vector embedding schema documentation
```

## 🐛 Reporting Issues

### Bug Reports
- Use the bug template
- Include steps to reproduce
- Attach logs/screenshots
- Specify Python version, OS, Azure SDK version

### Feature Requests
- Use the feature template
- Explain use case and expected behavior
- Reference relevant docs/issues
- Link to Phase roadmap if applicable

## 📚 Documentation Structure

- `/docs/` — Design & architecture documentation
- `README.md` — Project overview & quick start
- Inline comments — Code-level documentation
- Git commits — Change history

## 🚀 Release Process

1. Version bump in `pyproject.toml`
2. Update [CHANGELOG.md](CHANGELOG.md)
3. Create release PR
4. Tag release: `git tag v1.0.0`
5. GitHub Actions auto-publishes

## ❓ Questions?

- **Architecture questions:** See [SYSTEM_DESIGN_v3.0.md](/docs/SYSTEM_DESIGN_v3.0.md)
- **Agent implementation:** See [agent documentation](/docs/)
- **Timeline questions:** See [IMPLEMENTATION_ROADMAP.md](/docs/IMPLEMENTATION_ROADMAP.md)
- **Slack:** #newsroom-dev channel

## 📜 License

By contributing, you agree your work will be licensed under the MIT License (see [LICENSE](LICENSE)).

---

**Thank you for contributing to AAN! 🙌**
