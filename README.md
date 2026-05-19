# PGUI

A lightweight UI framework built on top of pygame, designed for developers who want to build simple PC games — such as visual novels, RPGs, and similar genres — without having to rebuild common UI and scene management systems from scratch.

> ⚠️ Currently supports PC only.

---

## Features

- **Ready-to-use UI components** — just import and use, no setup needed
- **Scene management** — push/pop scenes with a built-in manager
- **Extensible** — components are designed to be easily extended or styled

---

## UI Components

| Component | Description |
|---|---|
| `Alert` | Popup alert box |
| `Background` | Fullscreen or partial background renderer |
| `Button` | Clickable button with style support |
| `Checkbox` | Toggle checkbox input |
| `Dropdown` | Dropdown selection menu |
| `Grid` | Grid layout container |
| `Image` | Image renderer |
| `Input` | Text input field |
| `Label` | Static text label |
| `Panel` | Bordered container panel |
| `Radio` | Radio button group |
| `Scrollbar` | Scrollable area support |
| `Slider` | Range slider input |
| `Switch` | Toggle switch |
| `Tabs` | Tabbed navigation |
| `TextBox` | Multiline text display box |

---

## Requirements

- Python `3.12.3`
- pygame `2.6.1`
- numpy `2.4.4`

---

## Installation

**Using Git Clone**
```bash
git clone -b develop https://github.com/MeoMuop3727/pgui.git
cd pgui
pip install pygame==2.6.1 numpy==2.4.4
```

**Using Git Submodule** (for embedding in your own project)
```bash
git submodule add -b develop https://github.com/MeoMuop3727/pgui.git
git submodule update --init
```

---

## Quick Start

```python
import pygame
pygame.init()

from components.scences import *
from components.ui import *

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")

manager = ManageScence(screen)

class ScenceInit(Scence):
    def __init__(self, surface: pygame.Surface):
        super().__init__()
        self.__surface = surface
        self.__font = pygame.font.Font(None, 80)

        self.__label = Label(
            self.__surface,
            StyleLabel(
                content="My Game",
                color="#ffffff",
                pos=(300, 250),
                font=self.__font,
                size=(0, 0)
            )
        )

    def render(self, screen):
        screen.fill("#000000")
        self.__label.update()

manager.push_scence(ScenceInit(screen))
manager.run()
```

Each module includes a docstring with detailed usage examples for its specific component.

---

## Project Structure

```
pgui/
├── assets/         # Images, fonts, and other static resources
├── components/
│   ├── scences/    # Scene management and base scene classes
│   └── ui/         # UI components
├── config/         # Global configuration and constants
├── entities/       # Game or application entities
├── systems/        # Core systems logic
└── utils/          # Helper functions and type utilities
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

---

## License

MIT — see [LICENSE](LICENSE) for details.