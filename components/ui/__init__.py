"""
PGUI is a set of Python UI components designed for building game interfaces with pygame.
It is built on top of pygame and numpy, providing ready-to-use widgets such as buttons,
inputs, sliders, dropdowns, and more. Each component follows a consistent Style/Component
pattern, making it straightforward to customize and integrate into any pygame project.
"""

from components.ui.alert import Alert, StyleAlert
from components.ui.button import Button, ButtonImage, ButtonText, StyleButton
from components.ui.background import BackgroundImage
from components.ui.checkbox import CheckBox, CheckBoxList, StyleCheckBox
from components.ui.dropdown import Dropdown, StyleDropdown
from components.ui.grid import Grid, StyleGrid
from components.ui.image import Image, StyleImage
from components.ui.input import Input, StyleInput
from components.ui.label import Label, StyleLabel
from components.ui.panel import Panel, StylePanel
from components.ui.radio import RadioButton, RadioButtonList, StyleRadioButton
from components.ui.scrollbar import ScrollView, StyleScrollView
from components.ui.slider import Slider, StyleSlider
from components.ui.switch import StyleSwitch, Switch
from components.ui.tabs import StyleTab, Tab
from components.ui.textbox import StyleTextBox, TextBox

__all__ = [
    "Alert", "StyleAlert",
    "Button", "ButtonImage", "ButtonText", "StyleButton",
    "BackgroundImage",
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
