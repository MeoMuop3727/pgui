# Contributing to PGUI

Thank you for your interest in contributing to PGUI.

PGUI is a lightweight UI and utility framework built on top of pygame, focused on reusable architecture, clean project organization, and beginner-friendly development workflows.

---

# Requirements

- Python `3.12+`
- pip `24+`

Main dependencies are managed automatically through `pyproject.toml`.

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
- Install `pgui` in editable mode
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

# Project Structure

```txt
pgui/
│
├── pgui/
│   ├── assets/         # Fonts, images, static resources
│   ├── components/     # Reusable UI components
│   ├── scenes/         # Scene system and scene management
│   ├── systems/        # Core engine systems
│   ├── models/         # Core object models
│   ├── config/         # Framework configuration
│   ├── utils/          # Helper utilities
│   └── __init__.py
│
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore
```

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
3. Commit your changes clearly
4. Open a Pull Request targeting `develop`
5. Describe:
   - What changed
   - Why it changed
   - Screenshots or examples if applicable

---

# Code Style

PGUI currently follows general PEP8 conventions.

## Naming

| Type | Convention |
|---|---|
| Variables | `snake_case` |
| Functions | `snake_case` |
| Classes | `PascalCase` |
| Constants | `UPPER_CASE` |

---

## General Guidelines

- Keep functions small and focused
- Prefer composition over deeply coupled logic
- Add docstrings to public APIs
- Avoid hardcoded values when reusable constants are possible
- Keep modules responsibility-focused

---

# Reporting Issues

When reporting bugs, include:

- Clear description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version
- OS information

---

# Future Plans

Planned improvements include:

- Automated testing
- CI/CD workflows
- Documentation website
- Theme system
- Advanced UI layout system

---

Thank you for helping improve PGUI.