# PGUI

PGUI is a lightweight UI framework built on top of pygame, designed for developers who want to build small to medium-sized PC games — such as visual novels, RPGs, dialogue systems, and similar genres — without rebuilding common UI and scene management systems from scratch.

> ⚠️ Currently supports PC platforms only.

---

# Features

- Reusable UI components
- Built-in scene management system
- Lightweight and beginner-friendly architecture
- Extensible component design
- Easy integration into existing pygame projects

---

# Requirements

- Python `3.12+`
- pip `24+`

All required dependencies are installed automatically through `pyproject.toml`.

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

- Install all dependencies automatically
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

# Quick Start

```python
import pygame

pygame.init()

from pgui.scenes import *
from pgui.components.ui import *

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")

manager = SceneManager(screen)

class MainScene(Scene):
    def __init__(self, surface: pygame.Surface):
        super().__init__()

        self.surface = surface
        self.font = pygame.font.Font(None, 80)

        self.label = Label(
            self.surface,
            StyleLabel(
                content="My Game",
                color="#ffffff",
                pos=(300, 250),
                font=self.font,
                size=(0, 0)
            )
        )

    def render(self, screen):
        screen.fill("#000000")
        self.label.update()

manager.push_scene(MainScene(screen))
manager.run()
```

---

# Project Structure

```txt
pgui/
│
├── pgui/
│   ├── assets/         # Images, fonts, and static resources
│   ├── components/     # Reusable UI components
│   ├── scenes/         # Scene system and scene management
│   ├── systems/        # Core systems
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

# Documentation

Each public module contains inline docstrings and usage examples.

Additional documentation will be expanded in future releases.

---

# Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

# License

MIT License — see [LICENSE](LICENSE) for details.