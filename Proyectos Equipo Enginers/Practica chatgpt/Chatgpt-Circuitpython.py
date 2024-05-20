#Ricardo Rodriguez Ledesma
#Tijuana, Baja California a lunes 22 de mayo de 2023

import json
import os
import ssl
import traceback

import board
import busio
import displayio
import digitalio
import keypad
import socketpool
import supervisor
from wifi import radio

import adafruit_requests
import adafruit_displayio_ssd1306
from adafruit_bitmap_font.bitmap_font import load_font
from adafruit_display_text import wrap_text_to_pixels
from adafruit_display_text.bitmap_label import Label
from adafruit_ticks import ticks_add, ticks_less, ticks_ms


# Choose your own prompt and wait messages, either by changing it below inside
# the """triple quoted""" string, or by putting it in your settings.toml file,
# like so:
#
# MY_PROMPT="Give me an idea for a gluten free, keto dinner. Write one sentence"
# PLEASE_WAIT="Cooking something up just for you"
#
# Experimentation is best to figure out what works. Usually you'll want to ask
# for just one sentence or paragraph, since the 128x32 pixel screen can't hold
# much text!

# Here are some that the author found worked reasonably well:

# Give me an idea for a plant-based dinner. Write one sentence
#
# Give jepler (they/them) a cliched and flowery description as a comic book
# supervillain. write one sentence.
#
# Invent and describe an alien species. write one sentence
#
# Invent a zany 'as seen on' product that can't possibly work. One sentence
#
# Tell a 1-sentence story about a kitten and a funny mishap
#
# Make up a 1-sentence fortune for me
#
# In first person, write a 1-sentence story about an AI avoiding boredom in a creative way.
#
# Pick an everyday object (don't say what it is) and describe it using only the
# ten hundred most common words.
#
# Invent an alien animal or plant, name it, and vividly describe it in 1
# sentence
#
# Invent and vividly describe an alien species. write one paragraph

prompt=os.getenv("MY_PROMPT", """
Cuentame un dato curioso""").strip()
please_wait=os.getenv("Por favor, Espera un momento", """
Buscando....
""").strip()

openai_api_key = os.getenv("OPENAI_API_KEY")

nice_font = load_font("helvR08.pcf")
line_spacing = 9 # in pixels

#  i2c display setup
displayio.release_displays()
oled_reset = board.GP9

# STEMMA I2C on picowbell
sda, scl = board.GP16, board.GP17
i2c = busio.I2C(scl, sda)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c, reset=oled_reset)

WIDTH = 128
HEIGHT = 64

display = adafruit_displayio_ssd1306.SSD1306(
    display_bus, width=WIDTH, height=HEIGHT
)
if openai_api_key is None:
    input("Place your\nOPENAI_API_KEY\nin settings.toml")
display.auto_refresh = False

class WrappedTextDisplay(displayio.Group):
    def __init__(self):
        super().__init__()
        self.offset = 0
        self.max_lines = display.height // line_spacing
        for i in range(self.max_lines):
            self.make_label("", i * line_spacing)
        self.lines = [""]
        self.text = ""

    def make_label(self, text, y):
        result = Label(
            font=nice_font,
            color=0xFFFFFF,
            background_color=0,
            line_spacing=line_spacing,
            anchor_point=(0, 0),
            anchored_position=(0, y),
            text=text)
        self.append(result)

    def add_text(self, new_text):
        print(end=new_text)
        if self.lines:
            text = self.lines[-1] + new_text
        else:
            text = new_text
        self.lines[-1:] = wrap_text_to_pixels(text, display.width, nice_font)
        self.scroll_to_end()

    def set_text(self, text):
        print("\n\n", end=text)
        self.text = text
        self.lines = wrap_text_to_pixels(text, display.width, nice_font)
        self.offset = 0

    def show(self, text):
        self.set_text(text)
        self.refresh()

    def add_show(self, new_text):
        self.add_text(new_text)
        self.refresh()

    def scroll_to_end(self):
        self.offset = self.max_offset()

    def scroll_next_line(self):
        max_offset = self.max_offset()
        self.offset = (self.offset + 1) % (max_offset + 1)

    def max_offset(self):
        return max(0, len(self.lines) - self.max_lines)

    def on_last_line(self):
        return self.offset == self.max_offset()

    def refresh(self):
        lines = self.lines
        # update labels from wrapped text, accounting for scroll offset
        for i in range(len(self)):
            offset_i = i + self.offset
            if offset_i >= len(lines):
                text = ""
            else:
                text = lines[offset_i]
            if text != self[i].text:
                self[i].text = text

        # Actually update the display all at once
        display.refresh()

display.root_group = wrapped_text = WrappedTextDisplay()

def wait_button_scroll_text():
    led.switch_to_output(True)
    keys.events.clear()
    deadline = ticks_add(ticks_ms(),
            5000 if wrapped_text.on_last_line() else 1000)
    while True:
        if (event := keys.events.get()) and event.pressed:
            break
        if wrapped_text.max_offset() > 0 and ticks_less(deadline, ticks_ms()):
            wrapped_text.scroll_next_line()
            wrapped_text.refresh()
            deadline = ticks_add(deadline,
                    5000 if wrapped_text.on_last_line() else 1000)
    led.value = False

if radio.ipv4_address is None:
    wrapped_text.show(f"Conectando con {os.getenv('WIFI_SSID')}")
    radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))
requests = adafruit_requests.Session(socketpool.SocketPool(radio), ssl.create_default_context())

def iter_lines(resp):
    partial_line = []
    for c in resp.iter_content():
        if c == b'\n':
            yield (b"".join(partial_line)).decode('utf-8')
            del partial_line[:]
        else:
            partial_line.append(c)
    if partial_line:
        yield (b"".join(partial_line)).decode('utf-8')

full_prompt = [
    {"role": "user", "content": prompt},
]

keys = keypad.Keys((board.GP14,), value_when_pressed=False)
led = digitalio.DigitalInOut(board.GP10)
led.switch_to_output(False)

try:
    while True:
        wrapped_text.show(please_wait)

        with requests.post("https://api.openai.com/v1/chat/completions",
            json={"model": "gpt-3.5-turbo", "messages": full_prompt, "stream": True},
            headers={
                "Authorization": f"Bearer {openai_api_key}",
            },
            ) as response:

            wrapped_text.set_text("")
            if response.status_code != 200:
                wrapped_text.show(f"Uh oh! {response.status_code}: {response.reason}")
            else:
                wrapped_text.show("")
                for line in iter_lines(response):
                    led.switch_to_output(True)
                    if line.startswith("data: [DONE]"):
                        break
                    if line.startswith("data:"):
                        content = json.loads(line[5:])
                        try:
                            token = content['choices'][0]['delta'].get('content', '')
                        except (KeyError, IndexError) as e:
                            token = None
                        led.value = False
                        if token:
                            wrapped_text.add_show(token)
                wait_button_scroll_text()
except Exception as e: # pylint: disable=broad-except
    traceback.print_exception(e) # pylint: disable=no-value-for-parameter
    print(end="\n\n\nAn error occurred\n\nPress button\nto reload")
    display.root_group = displayio.CIRCUITPYTHON_TERMINAL
    display.auto_refresh = True
    while True:
        if (event1 := keys.events.get()) and event1.pressed:
            break
    supervisor.reload()
