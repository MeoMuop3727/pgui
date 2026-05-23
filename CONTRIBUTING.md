# Contributing to PGUI

Thank you for your interest in contributing to PGUI! This document outlines the guidelines for getting started and submitting contributions.

---

## Requirements

- Python `3.12.3`
- pygame `2.6.1`
- numpy `2.4.4`

---

## Installation

**Using Git Clone**
```bash
git clone -b main https://github.com/MeoMuop3727/pgui.git
cd pgui
pip install pygame==2.6.1 numpy==2.4.4
```

**Using Git Submodule** (for embedding in your own project)
```bash
git submodule add -b main https://github.com/MeoMuop3727/pgui.git pgui_module
git submodule update --init
```

---

## Project Structure

```
pgui/
├── assets/         # Images, fonts, and other static resources
├── components/
│   ├── scences/    # Scene management and base scene classes
│   └── ui/         # UI components (buttons, text boxes, etc.)
├── config/         # Global configuration and constants
├── models/         # Game or application entities
├── systems/        # Core systems logic
└── utils/          # Helper functions and type utilities
```

---

## Branching

| Branch | Purpose |
|---|---|
| `main` | Stable releases only |
| `develop` | Active development — use this as your base |

When contributing, **always branch off from `develop`**:

```bash
git checkout develop
git checkout -b feature/your-feature-name
```

Branch naming convention:
- `feature/` — new features
- `fix/` — bug fixes
- `docs/` — documentation changes
- `refactor/` — Refactor code

---

## Submitting a Pull Request

1. Fork the repository
2. Create a new branch from `develop`
3. Make your changes
4. Open a Pull Request targeting the `develop` branch
5. Describe clearly what your PR does and why

---

## Code Style

Currently follows basic [PEP8](https://peps.python.org/pep-0008/) conventions. A more detailed style guide will be defined in a future release.

Key points for now:
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Keep functions focused and small
- Add docstrings to public classes and methods

---

## Reporting Issues

If you find a bug or have a feature request, please open an issue with:
- A clear title
- Steps to reproduce (for bugs)
- Expected vs actual behavior