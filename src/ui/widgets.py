# Built-in modules
import re
import logging
from typing import List, Literal

# Requirements modules
from customtkinter import (
    CTkFrame,
    CTkToplevel,
    CTkButton,
    CTkTextbox,
    CTkEntry,
    CTkLabel
)

# Internal modules
from core.config import KeyboardSettings
from core.resource_manager  import FontLibrary, IconLibrary
from core.constants import TABLE_256COLORS

#~~~~~ BASE TEMPLATES ~~~~~#

class PopupWindow(CTkToplevel):
    """
    Template for a a child window of the main app.
    """
    def __init__(self, win_title: str, win_size: tuple, *args, **kw):
        # Initialize inherited class
        super().__init__(*args, **kw)
        self.title(win_title)
        self.geometry(f'{win_size[0]}x{win_size[1]}')

    def close(self):
        self.destroy()

class Sidebar(CTkFrame):
    """
    Module that create a sidebar with three containers :
    - A header at the top that can hold a logo
    - A menu with a vertical list of tab
    - A footer that is configurable
    """

    def __init__(self, parent, title: str | None = None, icon: str | None = None):
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))
        
        # Initialize inherited class
        super().__init__(parent)

        # Initialize instance variable
        self.tabs = {}
        self.selected = None

        # Show header if there is atleast title or icon parameter that has been set.
        self.set_header(title, icon)
        if title is not None or icon is not None:
            self.show_header()

        # Set the frame for the tab list
        self.menu = CTkFrame(self)
        self.menu.configure(fg_color='transparent', corner_radius=0)
        self.menu.pack(side='top', fill='both')

        # Set the frame for the footer
        self.footer = CTkFrame(self)
        self.footer.configure(fg_color='transparent', corner_radius=0)
        self.footer.pack(side='bottom', fill='both')

    def set_header(self, title: str = 'Brand', icon: str | None = None):
        """Set an icon OR a title in the header (can't be both, the icon will be prioritized)"""
        if icon is not None:
            txt = ''
            img = IconLibrary.Contents[icon].tkObject()
        else:
            txt = title
            img = None

        self.header = CTkLabel(
            self,
            text=txt,
            image=img,
            fg_color='transparent',
            font=('', 20, 'bold'),
            corner_radius=0
            )

    def show_header(self):
        self.header.pack(side='top', fill='both')

    def hide_header(self):
        self.header.pack_forget()

    def add_tab(self, ctkObject, name: str, icon: str, default: bool = False):
        """
        Add a tab to the widget.
        
        Parameters
        ----------
        content: Any
            Reference of the content that should be controlled by the tab
        name: str
            Set the name of the tab
        icon: str
            Set the icon of the tab. Use the name of the file without the extension.
        """
        # Add a new tab button
        self.tabs.update({name: TabButton(self.menu, ctkObject, name, icon)})

        # Binding accelerators
        self.tabs[name].bind('<Button-1>', lambda e: self._on_click_tab(e))

        # Draw the button
        self.tabs[name].pack(anchor='ne', side='top', expand=True, fill='x', padx=6, pady=3)

        if default:
            self.select_tab(name)

    def select_tab(self, tab_name):
        if tab_name is not self.selected:
            self.log.info("Selecting tab named \x1b[32m{}\x1b[0m".format(tab_name))

            # Iterate over the list of tabs
            for name in self.tabs:

                # Check if tab_name is matching
                if self.tabs[name].tab_name == tab_name:
                    self.selected = name
                    self.tabs[name].open_tab()
                else:
                    self.tabs[name].close_tab()

                self.tabs[name].update()

        else:
            self.log.info("Tab named \x1b[31m{}\x1b[0m is already opened".format(tab_name))

    def _on_click_tab(self, event):
        self.select_tab(event.widget.master.tab_name)

class TabButton(CTkButton):
    """Custom button for the tabs in the sidebar"""
    def __init__(self, parent, ctkObject, name: str, icon: str):
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        # Initialize inherited class
        super().__init__(parent)
        self.configure(
            text=name,
            font=FontLibrary.Contents['Inter Variable']['Regular'].tkObject(weight='bold'),
            image=IconLibrary.Contents[icon].tkObject(size=(20, 20)),
            fg_color='transparent',
            corner_radius=4,
            border_width=0,
            border_spacing=6,
            width=24,
            anchor='w'
        )

        # Initialize instance variable
        self.tab_name = name
        self.tab_panel = ctkObject

    def open_tab(self):
        self.configure(fg_color=('#9AA7B8', '#4E627A'))
        self.update() # Needed to avoid blinking when changing tab
        self.tab_panel.pack(anchor='nw', expand=True, fill='both', side='left', padx=8, pady=8)

    def close_tab(self):
        self.configure(fg_color='transparent')
        self.tab_panel.pack_forget()

class PanelTemplate(CTkFrame):
    """Base template for a panel including a header."""
    def __init__(self, parent, title: str, **kwargs):
        # Set instance logger
        self.log = logging.getLogger(self.__class__.__name__)

        # Initialize inherited class
        super().__init__(parent, **kwargs)

        # Adding header
        self.header = PanelHeader(self, title=title, fg_color=self._fg_color)
        self.header.pack(anchor='nw', fill='x', side='top', padx=10, pady=8)

class PanelHeader(CTkFrame):
    """
    Create a header for a panel.
    Labels are put to the left and Buttons are put to the right.
    It's best to keep the same shape of button (text or icon only) for keeping a good layout.
    """
    def __init__(self, parent, title: str, *args, **kwargs):
        # Initialize inherited class
        super().__init__(parent, *args, **kwargs)
        self.configure(corner_radius=0)

        # Initialize instance variable
        self.buttons = []

        # Set the title of the header
        self.title = CTkLabel(self, text=title, font=FontLibrary.Contents['Inter Variable']['Regular'].tkObject(size=18), anchor='w')
        self.title.pack(anchor='w', expand=True, side='left', fill='x', padx=2)

        # Set the frame for holding the different buttons
        self.button_frame = CTkFrame(self, height=1, fg_color='transparent')
        self.button_frame.pack(anchor='w', side='right')

class ButtonHeader(CTkButton):
    def __init__(self, parent, text: str | None = None, icon_name: str = 'home', icon_size: int = 16, **kwargs):
        # Reduce the width of the widget to the icon size if there is no text. Else return the width
        if text is None:
            width = icon_size + 4
        else:
            width = kwargs.pop('width') | 140

        # Initialize inherited class
        super().__init__(
            master=parent,
            text=text,
            image=IconLibrary.Contents[icon_name].tkObject(size=(icon_size, icon_size)),
            width=width,
            **kwargs
            )

class TextStream(CTkTextbox):
    """
    Custom text box widget that try to imitate the console style.
    Support ANSI encoding.
    The widget works like a stream with `write` and `flush` functions.

    List of supported SGR parameters
    --------------------------------
    |n|Name|
    |-|----|
    |0|Reset|
    |4|Underline|
    |9|Crossed-out|
    |24|Not underline|
    |29|Not croseed out|
    |30-37|Set foreground color|
    |38|Set foreground color (8-bit or 24-bit)|
    |39|Default foreground color|
    |40-47|Set background color|
    |48|Set background color (8-bit or 24-bit)|
    |49|Default background color|
    |90-97|Set light foreground color|
    |100-107|Set light background color|
    """
    def __init__(self, parent):
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        # Initialize inherited class
        super().__init__(parent)
        self.configure(
            font=FontLibrary.Contents['Source Code Pro']['Regular'].tkObject(size=12),
            insertwidth=0 # To avoid seeing the caret in the textbox
        )

        # Replace keyboard events to made it read-only andget some function
        self.bind('<Key>', lambda e: self._keyEvent(e))

        # Initialize instance variables
        self.ansi_tags = []
        self.ansi_regex = re.compile(r"\x1b?\033?\[([\d+;]*)m")
        self.ansi_code_style = {'format' : {4: 'underline',  9: 'overstrike'},
                                'reset' : {24: 'underline', 29: 'overstrike'}}
        self.ansi_code_color = {'foreground': {38: 'fg-custom', 39: 'fg-default'},
                                'background': {48: 'bg-custom', 49: 'bg-default'}}

        # Configure tag for styling
        self.tag_config('underline', underline=True)
        self.tag_config('overstrike', overstrike=True)

        # Set the list of tags for 4-bits colors
        colors_dark = ['black', 'maroon', 'green', 'olive', 'darkblue', 'darkmagenta', 'darkcyan', 'gray70']
        colors_light = ['gray30', 'red', 'lime', 'yellow', 'blue', 'magenta', 'cyan', 'white']

        # Configure corresponding code to tag for 4-bits colors
        for idx, (dark, light) in enumerate(zip(colors_dark, colors_light)):
            self.ansi_code_color['foreground'][30+idx] = 'fg-{}'.format(dark)
            self.tag_config(self.ansi_code_color['foreground'][30+idx], foreground=dark)

            self.ansi_code_color['background'][40+idx] = 'bg-{}'.format(dark)
            self.tag_config(self.ansi_code_color['background'][40+idx], background=dark)

            self.ansi_code_color['foreground'][90+idx] = 'fg-{}'.format(light)
            self.tag_config(self.ansi_code_color['foreground'][90+idx], foreground=light)

            self.ansi_code_color['background'][100+idx] = 'bg-{}'.format(light)
            self.tag_config(self.ansi_code_color['background'][100+idx], background=light)

    def write(self, text, tags=None):  # noqa: F811
        if self.ansi_regex.search(text) is not None:
            for codes, new_span, delta, string in self.find_ansi_codes(text):

                # Decoding ANSI code to tags
                self.update_ansi_tags(codes)
                tag_list = self.ansi_tags

                # Add additional tags when the function is called
                if tags is not None:
                    if isinstance(tags, str):
                        tag_list.insert(0, tags)
                    elif isinstance(tags, list) or isinstance(tags, tuple):
                        tag_list.insert(0, tags)

                self.insert('end', string, tag_list)
        self.yview('end')

    def flush(self):
        self.delete(1.0, 'end')

    def find_ansi_codes(self, text):  # noqa: F811
        """Iterate over a string to find one or more ANSI code."""
        text_no_tag, tag_count = self.ansi_regex.subn('', text)

        # Initialize variables
        codes = []
        tag_start = None
        tag_end = None
        delta = 0
        delta_total = 0

        for idx, match in enumerate(self.ansi_regex.finditer(text), 1):

            if idx == tag_count:
                tag_end = match.start() - delta_total
                yield codes, (tag_start, tag_end), delta, text_no_tag[tag_start:tag_end]

                if tag_end < len(text_no_tag):
                    codes = [int(code) for code in match.group(1).split(';')]
                    delta = match.end() - match.start()
                    tag_start = tag_end
                    tag_end = len(text_no_tag)
                    yield codes, (tag_start, tag_end), delta, text_no_tag[tag_start:tag_end]

            elif idx == 1:
                # If the first match is not starting at 0, we record the first part of the string without formatting it.
                if match.start() > 0:
                    yield None, (0, match.start()), None, text_no_tag[0:match.start()]
                
                # We retrieve the start of the first tag without constructing the record.
                # We need to retrieve the next tag to set the end of the tag, so we skip to the next.
                codes = [int(code) for code in match.group(1).split(';')]
                delta = match.end() - match.start()
                tag_start = match.start()
                delta_total += delta
                continue

            else:
                # Setting the end of the previous match with the end index of the actual match
                tag_end = match.start() - delta_total
                yield codes, (tag_start, tag_end), delta, text_no_tag[tag_start:tag_end]

                # Setting the start of the actual match
                codes = [int(code) for code in match.group(1).split(';')]
                delta = match.end() - match.start()
                tag_start = match.start() - delta_total
                delta_total += delta

    def update_ansi_tags(self, codes: list | None = None):
        """
        Convert ANSI code into tag. Return a full list of tags.
        """

        if codes is None:
            print(codes)
            self.reset_style()
            self.reset_color('fg')
            self.reset_color('bg')
            return

        for code in codes:
            if code == 0:
                self.reset_style()
                self.reset_color('fg')
                self.reset_color('bg')

            elif code == 38:
                self.set_custom_color('fg', codes[1:-1])
                return

            elif code == 48:
                self.set_custom_color('bg', codes[1:-1])
                return

            elif code == 39:
                self.reset_color('fg')

            elif code == 49:
                self.reset_color('bg')

            elif 1 <= code <= 9:
                self.set_style(code)

            elif 20 <= code <= 29:
                self.remove_style(code)

            elif 30 <= code <= 39:
                self.set_color('fg', code)

            elif 40 <= code <= 49:
                self.set_color('bg', code)

            elif 90 <= code <= 99:
                self.set_color('fg', code)

            elif 100 <= code <= 109:
                self.set_color('bg', code)

    def set_style(self, code: int | None = None):
        if self.ansi_code_style['format'].get(code, None) is not None:
            try:
                new_tag = self.ansi_code_style['format'][code]
            except IndexError:
                self.log.error("Can't find the correspond code in the ANSI table", exc_info=True)
                return

        # Check if tag is already present
        if new_tag not in self.ansi_tags:
            self.ansi_tags.append(new_tag)

    def remove_style(self, code: int | None = None):
        # Check if tag is already present
        try:
            self.ansi_tags.remove(self.ansi_code_style['reset'][code])
        except ValueError:
            self.log.error('ANSI style tag ')

    def reset_style(self):
        for tag in enumerate(self.ansi_code_style):
            try:
                self.ansi_tags.remove(tag)
            except ValueError:
                None

    def set_color(self, layer: Literal['fg', 'bg'], code: int | None = None):
        # Retrieve tags in ansi code list
        match layer:
            case 'fg':
                new_tag = self.ansi_code_color['foreground'][code]
            case 'bg':
                new_tag = self.ansi_code_color['background'][code]

        # Check if tag is already present
        if new_tag not in self.ansi_tags:
            self.reset_color(layer)
            self.ansi_tags.append(new_tag)

    def reset_color(self,  layer: Literal['fg', 'bg']):
        for index, tag in enumerate(self.ansi_tags):
            if tag.startswith('{}-'.format(layer)):
                self.ansi_tags.pop(index)

    def set_custom_color(self, layer: Literal['fg', 'bg'], codes: list[int] | None = None):
        # When using 256 colors
        if codes[0] == 2:
            color_value = codes[1]
            new_tag = self.decode_custom_color(layer, color_value)

        # When using 24-bit colors
        elif codes[0] == 5:
            rgb = []
            for channel_value in codes[1:-1]:
                rgb.append(channel_value)
            new_tag = self.decode_custom_color(layer, rgb)

        # Check if tag is already present
        if new_tag not in self.ansi_tags:
            self.reset_color(layer)
            self.ansi_tags.append(new_tag)

    def decode_custom_color(self, layer: Literal['fg', 'bg'], codes: int | List[int]):
        """
        Return the associated custom color tag.\n
        If not available, automatically create the corresponding tag.
        """
        rgb_val = [0, 0, 0]
        rgb_hex = ['00', '00', '00']
        
        # For 256 colors
        if isinstance(codes, int):
            # Retrieve color values
            for idx, channel_value in enumerate(TABLE_256COLORS[codes]):
                rgb_val[idx] = channel_value
                rgb_hex[idx] = channel_value.to_bytes(4, "big").hex()
            
            # Format name of tag
            tag_name = '{}-c{}'.format(layer, rgb_val[0])
        
        # For 24-bit colors
        elif isinstance(codes, list):
            # Retrieve color values
            for idx, channel_value in enumerate(codes):
                rgb_val[idx] = channel_value
                rgb_hex[idx] = channel_value.to_bytes(1).hex()
            
            # Format name of tag
            tag_name = '{}-r{}g{}b{}'.format(layer, rgb_val[0], rgb_val[1], rgb_val[2])

        # Retrieve hexadecimal string
        tag_color = '#{}{}{}'.format(rgb_hex[0], rgb_hex[1], rgb_hex[2])

        # Check if custom tag is already configurated, if not, register it.
        if tag_name not in self.tag_names():
            match layer:
                case 'fg':
                    self.tag_config(tagName=tag_name, foreground=tag_color)
                    return tag_name

                case 'bg':
                    self.tag_config(tagName=tag_name, background=tag_color)
                    return tag_name

        if tag_name in self.tag_names():
            return tag_name

    def _keyEvent(self, event):
        """
        Replace the classic binding of the Text object when all key presses are ignored.
        Give access to some accelerators like saving to clipboard (Ctrl + C) a part of the content by selecting it.
        Trying to be the most compatible between OS, but not all have been cleared of problems.
        """

        try:
            # If Control-C is fired, save selected text to clipboard
            if event.state == KeyboardSettings.get_control_state() and KeyboardSettings.get_regex_key_characters('key-c').findall(event.char):
                self._accelerator_copySelection()

            # If Tab is fired, focus to next widget
            elif event.keysym == 'Tab':
                self.tk_focusNext().focus_set()

        finally:
            # This is here to replace the input key by nothing.
            # If this is not there, every input will be writed in the text box!
            return "break"

    def _accelerator_copySelection(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.selection_get())
        except Exception:
            # To stop filling the stderr when there is no selection in the text box.
            pass

class EntryConsole(CTkEntry):
    """
    A Tkinter Entry widget that provides a way to send command.

    To Do
    -----
    - Send command to Python interpreter for MVP.
    - Create a button to select where the interpreter should send the command (Python, ADB, others...)
    """

    def __init__(self, parent, *args, **kw):
        # Initialize inherited class
        super().__init__(parent, *args, **kw)
        self.configure(
            font=FontLibrary.Contents['Source Code Pro']['Regular'].tkObject(size=12)
        )

        # Binding event handlers
        self.bind('<Return>', lambda e: self._keyEvent(e))

    def send_command(self):
        """NOT WORKING! Just an example with a print into stdout."""
        try:
            print('>>>', self.get())
            self.delete('0', 'end')
            return "break"
        except Exception:
            pass # To stop filling the stderr when there is no selection in the text box

    def _keyEvent(self, event):
        # If Return is fired, print command to console (TEST)
        if event.keysym == 'Return':
            self.send_command()



class CasqueWidget(CTkFrame):
    """
    Widget personnalisé pour afficher les informations et les actions d'un casque.
    """
    def __init__(self, parent, name, model, battery, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color="#D6D9DC", corner_radius=10)  # Configure the appearance

        # Affichage des informations du casque
        self.name_label = CTkLabel(self, text=name, width=150, anchor="w")
        self.name_label.pack(side="left", padx=10, pady=5)

        self.model_label = CTkLabel(self, text=model, width=100, anchor="w")
        self.model_label.pack(side="left", padx=10, pady=5)

        self.battery_label = CTkLabel(self, text=f"Batterie: {battery}", width=60, anchor="w")
        self.battery_label.pack(side="left", padx=10, pady=5)

        # Boutons pour interagir avec le casque
        self.open_button = CTkButton(self, text="Ouvrir", command=self.open_casque, width=80)
        self.open_button.pack(side="left", padx=5)

        self.close_button = CTkButton(self, text="Fermer", command=self.close_casque, width=80)
        self.close_button.pack(side="left", padx=5)

        self.refresh_button = CTkButton(self, text="Rafraîchir", command=self.refresh_casque, width=80)
        self.refresh_button.pack(side="left", padx=5)

    def open_casque(self):
        print(f"Ouverture de {self.name_label.cget('text')}")

    def close_casque(self):
        print(f"Fermeture de {self.name_label.cget('text')}")

    def refresh_casque(self):
        print(f"Rafraîchissement du {self.name_label.cget('text')}")
