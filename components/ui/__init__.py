"""
PGUI is a set of Python UI components designed for building game interfaces with pygame.
It is built on top of pygame and numpy, providing ready-to-use widgets such as buttons,
inputs, sliders, dropdowns, and more. Each component follows a consistent Style/Component
pattern, making it straightforward to customize and integrate into any pygame project.
"""

from .alert import Alert, StyleAlert
from .button import Button, ButtonImage, ButtonText, StyleButton
from .checkbox import CheckBox, CheckBoxList, StyleCheckBox
from .dropdown import Dropdown, StyleDropdown
from .grid import Grid, StyleGrid
from .image import Image, StyleImage
from .input import Input, StyleInput
from .label import Label, StyleLabel
from .panel import Panel, StylePanel
from .radio import RadioButton, RadioButtonList, StyleRadioButton
from .scrollbar import ScrollView, StyleScrollView
from .slider import Slider, StyleSlider
from .switch import StyleSwitch, Switch
from .tabs import StyleTab, Tab
from .textbox import StyleTextBox, TextBox

__all__ = [
    "Alert", "StyleAlert",
    "Button", "ButtonImage", "ButtonText", "StyleButton",
    "CheckBox", "CheckBoxList", "StyleCheckBox",
    "Dropdown", "StyleDropdown",
    "Grid", "StyleGrid",
    "Image", "StyleImage",
    "Input", "StyleInput",
    "Label", "StyleLabel",
    "Panel", "StylePanel",
    "RadioButton", "RadioButtonList", "StyleRadioButton",
    "ScrollView", "StyleScrollView",
    "Slider", "StyleSlider",
    "StyleSwitch", "Switch",
    "StyleTab", "Tab",
    "StyleTextBox", "TextBox",
]
