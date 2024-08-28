# Internal modules
from core.config import KeyboardSettings
from core.resource import FontLibrary
from core.constants import TABLE_256COLORS

# Requirements modules
from customtkinter import (
    CTkTextbox,
    CTkEntry
)

# Built-in modules
import re
import logging
from typing import List, Literal


class ConsoleStream(CTkTextbox):
    """
    Custom text box widget that try to imitate the console style.
    Support ANSI encoding.
    The widget works like a stream with `emit` and `flush` functions.

    You can configure other tags as any other Tkinter Textbox. But you should avoid those names :
    underline, overstrike, fg-custom, fg-default, bg-custom, bg-default.

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
        """
        Create a new ConsoleStream widget

        Parameters
        ----------
        parent : `Any`
            Set the parent widget
        """
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        # Initialize inherited class
        super().__init__(parent)
        self.configure(
            font=FontLibrary.get_font_tkinter('Source Code Pro', 'Regular', 12),
            insertwidth=0 # To avoid seeing the caret in the textbox
        )

        # Replace keyboard events to made it read-only and replace clipboard behavior
        self.bind('<Key>', lambda e: self._on_key_event(e))

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

    def emit(self, text, tags = None):  # noqa: F811
        """
        Write the string to the textbox (work like a streamHandler)

        Search if there is any ANSI code and loop over every code to bind the corresponding color tag.
        Auto-scroll to the end of the string that was added.

        Parameters
        ----------
        text : `Any`
            The text to insert in the textbox.
        tags : `Any`, optional
            Additionnal tag to add for the entire string. By defaults to None.
        """

        # Check if there is an ANSI code in the string
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

    def clear(self):
        """
        Delete all the data in the textbox.
        """

        self.delete(1.0, 'end')

    def find_ansi_codes(self, text: str):  # noqa: F811
        """
        Iterate over a string to find one or more ANSI codes.

        Parameters
        ----------
        text : `str`
            The text where to search for ANSI codes.

        Yields
        ------
        codes : `list | None`
            List of ANSI code that has been parsed into a `list` object
        tag_position : `Tuple[int, int]`
            Indicate the position that the ANSI code is influencing.
            As we remove the ANSI code, we take account of the total characters that was remove to get the correct position.
        delta : `int | None`
            The difference between the beginning and end of the code
        text_part : `str`
            The section of string that would be influenced by the actual ANSI code
        """
        # We use Regex method subn() taht is a substitution.
        # It's deleting ANSI code, returns a text without code
        text_without_ansi, code_count = self.ansi_regex.subn('', text)

        # Initialize variables
        codes = []
        tag_start = None
        tag_end = None
        delta = 0
        delta_total = 0

        # We go over each individual ANSI code that has been found.
        # Each match will be decomposed to retrieve informations.
        for idx, match in enumerate(self.ansi_regex.finditer(text), 1):

            # When it is the last code within the text, we need to take account of the last
            # ANSI code that could exist at the end of the string.
            if idx == code_count:
                tag_end = match.start() - delta_total
                yield codes, (tag_start, tag_end), delta, text_without_ansi[tag_start:tag_end]

                # If there is some string before the last characters,
                # we need to yield the last bit of string.
                if tag_end < len(text_without_ansi):
                    codes = [int(code) for code in match.group(1).split(';')]
                    delta = match.end() - match.start()
                    tag_start = tag_end
                    tag_end = len(text_without_ansi)
                    yield codes, (tag_start, tag_end), delta, text_without_ansi[tag_start:tag_end]

            # For the first code that was found, we only get partial information.
            # The next code will permit to register that fulle information, as we need
            # the start position of the next tag to know what the first tag is formatting.
            elif idx == 1:
                # If the first match is not starting at 0, we yield result of the first part of the string.
                if match.start() > 0:
                    yield None, (0, match.start()), None, text_without_ansi[0:match.start()]
                
                # We register the start of the first tag without constructing the record.
                # We need to retrieve the next tag to set the end of the tag, so we skip to the next.
                codes = [int(code) for code in match.group(1).split(';')]
                delta = match.end() - match.start()
                tag_start = match.start()
                delta_total += delta
                continue

            else:
                # Setting the end of the previous match with the end index of the actual match and yield result
                tag_end = match.start() - delta_total
                yield codes, (tag_start, tag_end), delta, text_without_ansi[tag_start:tag_end]

                # Setting the start of the actual match
                codes = [int(code) for code in match.group(1).split(';')]
                delta = match.end() - match.start()
                tag_start = match.start() - delta_total
                delta_total += delta

    def update_ansi_tags(self, codes: list[int] | None = None):
        """
        Call the corresponding functions to the ANSI codes list that was given.
        Each function will update the tag list `ansi_tags` from the instanciated object.

        Parameters
        ----------
        codes : `list[int]`, optional
            The list of ANSI code to use. By defaults to None.
        """

        if codes is None:
            print(codes)
            self.reset_styles()
            self.reset_colors('fg')
            self.reset_colors('bg')
            return

        for code in codes:
            if code == 0:
                self.reset_styles()
                self.reset_colors('fg')
                self.reset_colors('bg')

            elif code == 38:
                self.set_custom_color('fg', codes[1:-1])
                return

            elif code == 48:
                self.set_custom_color('bg', codes[1:-1])
                return

            elif code == 39:
                self.reset_colors('fg')

            elif code == 49:
                self.reset_colors('bg')

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
        """
        Retrieve the style tag corresponding to the ANSI code and append it to the tag list.

        Parameters
        ----------
        code : `int`, optional
            The ANSI code to convert. Defaults to None.
        """

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
        """
        Retrieve the style tag corresponding to the ANSI code and remove it from the tag list.

        Parameters
        ----------
        code : `int`, optional
            The ANSI code to convert. Defaults to None.
        """

        # Check if tag is already present
        try:
            self.ansi_tags.remove(self.ansi_code_style['reset'][code])
        except ValueError:
            self.log.error('ANSI style tag is not present')

    def reset_styles(self):
        """
        Remove all remaining style tags in the tag list.
        """

        for tag in enumerate(self.ansi_code_style):
            try:
                self.ansi_tags.remove(tag)
            except ValueError:
                None

    def set_color(self, layer: Literal['fg', 'bg'], code: int | None = None):
        """
        Retrieve the color tag corresponding to the ANSI code and append it to the tag list.

        Parameters
        ----------
        layer : `Literal['fg', 'bg']`
            Set the corresponding layer to activate. Foreground (fg) or background (bg).
        code : `int`, optional
            The ANSI code to convert. Defaults to None.
        """

        # Retrieve tags in ansi code list
        match layer:
            case 'fg':
                new_tag = self.ansi_code_color['foreground'][code]
            case 'bg':
                new_tag = self.ansi_code_color['background'][code]

        # Check if tag is already present
        if new_tag not in self.ansi_tags:
            self.reset_colors(layer)
            self.ansi_tags.append(new_tag)

    def reset_colors(self,  layer: Literal['fg', 'bg']):
        """
        Remove all remaining color tags of the selected layer in the tag list.

        Parameters
        ----------
        layer : `Literal['fg', 'bg']`
            Set the corresponding layer to activate. Foreground (fg) or background (bg).
        """

        for index, tag in enumerate(self.ansi_tags):
            if tag.startswith('{}-'.format(layer)):
                self.ansi_tags.pop(index)

    def set_custom_color(self, layer: Literal['fg', 'bg'], codes: list[int] | None = None):
        """
        Retrieve the custom color tag corresponding to the ANSI code and append it to the tag list.

        Parameters
        ----------
        layer : `Literal['fg', 'bg']`
            Set the corresponding layer to activate. Foreground (fg) or background (bg).
        codes : `list[int]`, optional
            The ANSI code list to convert. Defaults to None.
        """

        # When using 8-bit representation
        if codes[0] == 2:
            color_value = codes[1]
            new_tag = self.decode_custom_color(layer, color_value)

        # When using 24-bit representation
        elif codes[0] == 5:
            rgb = []
            for channel_value in codes[1:-1]:
                rgb.append(channel_value)
            new_tag = self.decode_custom_color(layer, rgb)

        # Check if tag is already present
        if new_tag not in self.ansi_tags:
            self.reset_colors(layer)
            self.ansi_tags.append(new_tag)

    def decode_custom_color(self, layer: Literal['fg', 'bg'], codes: int | List[int]):
        """
        Retrieve the custom color tag corresponding to the ANSI code color list.\n
        If not available, automatically create the corresponding tag.

        Can work with 256 colors (1 value as int) or in 24-bit colors (RGB value as list of 3 int).

        Parameters
        ----------
        layer : `Literal['fg', 'bg']`
            Set the corresponding layer to activate. Foreground (fg) or background (bg).
        codes : `list[int]`, optional
            The ANSI code list of color to convert. Defaults to None.
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

    def _on_key_event(self, event):
        """
        Replace the classic binding of the Text object when all key presses are ignored.
        Give access to some accelerators like saving to clipboard (Ctrl + C) a part of the content by selecting it.
        Trying to be the most compatible between OS, but not all have been cleared of problems.
        """

        try:
            # If Control-C is fired, save selected text to clipboard
            if event.state == KeyboardSettings.get_control_state() and KeyboardSettings.get_regex_key_characters('key-c').findall(event.char):
                self._on_copy_selection()

            # If Tab is fired, focus to next widget
            elif event.keysym == 'Tab':
                self.tk_focusNext().focus_set()

        finally:
            # This is here to replace the input key by nothing.
            # If this is not there, every input will be writed in the text box!
            return "break"

    def _on_copy_selection(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.selection_get())
        except Exception:
            # To stop filling the stderr when there is no selection in the text box.
            pass

class ConsoleEntry(CTkEntry):
    """
    A Tkinter Entry widget that provides a way to send command.\n
    *Very Not Finished!*

    To Do
    -----
    - Send command to Python interpreter for MVP.
    - Create a button to select where the interpreter should send the command (Python, ADB, others...)
    """

    def __init__(self, parent, **kwargs):
        # Initialize inherited class
        super().__init__(parent, **kwargs)
        self.configure(
            font=FontLibrary.get_font_tkinter('Source Code Pro', 'Regular', 12)
        )

        # Binding event handlers
        self.bind('<Return>', lambda e: self._on_key_event(e))

    def send_command(self):
        """NOT WORKING! Just an example with a print into stdout."""
        try:
            print('>>>', self.get())
            self.delete('0', 'end')
            return "break"
        except Exception:
            pass # To stop filling the stderr when there is no selection in the text box

    def _on_key_event(self, event):
        # If Return is fired, print command to console (TEST)
        if event.keysym == 'Return':
            self.send_command()