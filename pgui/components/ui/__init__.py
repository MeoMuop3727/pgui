"""
PGUI is a set of Python UI components designed for building game interfaces with pygame.
It is built on top of pygame and numpy, providing ready-to-use widgets such as buttons,
inputs, sliders, dropdowns, and more. Each component follows a consistent Style/Component
pattern, making it straightforward to customize and integrate into any pygame project.
"""

from pgui.components.ui.alert import Alert, StyleAlert
from pgui.components.ui.button import Button, ButtonImage, ButtonText, StyleButton
from pgui.components.ui.background import BackgroundImage
from pgui.components.ui.checkbox import CheckBox, CheckBoxList, StyleCheckBox
from pgui.components.ui.dropdown import Dropdown, StyleDropdown
from pgui.components.ui.dialog import Dialog
from pgui.components.ui.grid import Grid, StyleGrid
from pgui.components.ui.image import Image, StyleImage
from pgui.components.ui.input import Input, StyleInput
from pgui.components.ui.label import Label, StyleLabel
from pgui.components.ui.panel import Panel, StylePanel
from pgui.components.ui.radio import RadioButton, RadioButtonList, StyleRadioButton
from pgui.components.ui.scrollbar import ScrollView, StyleScrollView
from pgui.components.ui.slider import Slider, StyleSlider
from pgui.components.ui.switch import StyleSwitch, Switch
from pgui.components.ui.tabs import StyleTab, Tab
from pgui.components.ui.textbox import StyleTextBox, TextBox

__all__ = [
    "Alert", "StyleAlert",
    "Button", "ButtonImage", "ButtonText", "StyleButton",
    "BackgroundImage",
    "CheckBox", "CheckBoxList", "StyleCheckBox",
    "Dropdown", "StyleDropdown",
    "Dialog",
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
