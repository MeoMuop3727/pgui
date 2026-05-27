# Contributing to PGUI

Thank you for your interest in contributing to PGUI.

PGUI is a lightweight UI framework built on top of pygame, focused on reusable architecture, clean project organization, and beginner-friendly development workflows.

---

# Requirements

- Python `3.12+`
- pip `24+`

All dependencies are managed automatically through `pyproject.toml`.

---

# Repository Structure

PGUI follows the standard Python package layout.

```txt
pgui/
│
├── pgui/                 # Main Python package
│   ├── assets/
│   ├── components/
│   ├── config/
│   ├── models/
│   ├── scenes/
│   ├── systems/
│   ├── utils/
│   └── __init__.py
│
├── tests/                # Testing modules
├── pyproject.toml        # Package configuration
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore
```

Notes:

- The outer `pgui/` directory is the repository root
- The inner `pgui/` directory is the actual Python package
- All importable source code must remain inside the inner package directory

Example:

```python
from pgui.components.ui import *
```

---

# Installation

## Clone Repository

```bash
git clone -b develop https://github.com/MeoMuop3727/pgui.git
cd pgui
```

---

## Create Virtual Environment (Recommended)

### Linux / WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## Install PGUI

```bash
pip install -e .
```

This command will:

- Install all required dependencies automatically
- Register the `pgui` package locally
- Enable editable development mode
- Reflect source code changes instantly without reinstalling

---

# Using as a Git Submodule

PGUI can also be embedded directly into another project.

```bash
git submodule add -b develop https://github.com/MeoMuop3727/pgui.git libs/pgui
git submodule update --init --recursive
```

Then install locally:

```bash
pip install -e ./libs/pgui
```

---

# Shared Virtual Environment (Optional)

PGUI works well with a shared virtual environment workflow.

Example:

```bash
python3 -m venv ~/python-envs/game-dev
source ~/python-envs/game-dev/bin/activate
```

Then install PGUI into that environment:

```bash
pip install -e .
```

This avoids reinstalling dependencies across multiple projects.

---

# Branch Workflow

| Branch | Purpose |
|---|---|
| `main` | Stable releases |
| `develop` | Active development |

Always branch from `develop`.

```bash
git checkout develop
git checkout -b feature/your-feature-name
```

---

# Branch Naming Convention

| Prefix | Purpose |
|---|---|
| `feature/` | New feature |
| `fix/` | Bug fix |
| `docs/` | Documentation |
| `refactor/` | Refactor existing code |
| `test/` | Testing related changes |

Examples:

```txt
feature/button-animation
fix/input-focus
docs/update-readme
```

---

# Pull Request Guidelines

1. Fork the repository
2. Create a branch from `develop`
3. Commit changes clearly and consistently
4. Open a Pull Request targeting `develop`
5. Describe:
   - What changed
   - Why it changed
   - Screenshots/examples if applicable

---

# Code Style

PGUI currently follows general PEP8 conventions.

## Naming Conventions

| Type | Convention |
|---|---|
| Variables | `snake_case` |
| Functions | `snake_case` |
| Classes | `PascalCase` |
| Constants | `UPPER_CASE` |

---

## General Guidelines

- Keep functions small and focused
- Prefer composition over tightly coupled logic
- Add docstrings to public APIs
- Avoid unnecessary global state
- Keep modules responsibility-focused
- Prefer reusable systems over hardcoded behaviors

---

# Reporting Issues

When reporting bugs, include:

- Clear description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version
- Operating system information

---

# Future Plans

Planned improvements include:

- Automated testing
- CI/CD workflows
- Documentation website
- Theme system
- Advanced UI layout system
- Animation utilities
- Layout containers

---

Thank you for helping improve PGUI.