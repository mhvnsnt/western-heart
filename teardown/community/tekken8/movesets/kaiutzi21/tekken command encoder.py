# ================================
# Script: tekken_command_encoder.py
# Author: Kaiutzi21
# GitHub: github.com/kaiutzi21
# Created: 2025-07-20
# Description: Small web-based overlay to help generate and copy Commands
# ================================


# NOTE TO SELF: Convert this script into an executable with PyInstaller for easy distribution


import threading
import webbrowser

from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <title>Tekken Command Encoder</title>
    <style>
      body { font-family: sans-serif; padding: 2rem; }
      input, select { margin-bottom: 1rem; padding: 0.5rem; width: 200px; }
    </style>
  </head>
  <body>
    <h1>Tekken Command Encoder</h1>
    <form method="post">
      <label>Input Mode (MM):</label><br>
      <input type="text" name="mode" value="0x00"><br>

      <label>Buttons to NOT Hold (NN):</label><br>
      <input type="text" name="not_hold" value="0x00"><br>

      <label>Buttons to Hold (HH):</label><br>
      <input type="text" name="hold" value="0x00"><br>

      <label>Buttons to Press (PP):</label><br>
      <input type="text" name="press" value="0x00"><br>

      <label>Directional Input:</label><br>
      <input type="text" name="direction" value="0x00"><br>

      <button type="submit">Generate</button>
    </form>

    {% if result %}
      <h2>Ergebnis:</h2>
      <p><strong>{{ result }}</strong></p>
    {% endif %}
  </body>
</html>
"""

def encode_button_input(mode: int, not_hold: int, hold: int, press: int) -> int: 
    return (mode << 24) | (not_hold << 16) | (hold << 8) | press  # Encodes the button input into a single integer

def encode_command_value(button_input: int, directional_input: int) -> str:
    return f"0x{button_input:08X}{directional_input:08X}"   # Combines button input and directional input into final command value

_tag = bytes([0x4B, 0x61, 0x69, 0x75, 0x74, 0x7A, 0x69, 0x32, 0x31])

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:                                                # Parse hex inputs from the form
            mode = int(request.form['mode'], 16)            
            not_hold = int(request.form['not_hold'], 16)
            hold = int(request.form['hold'], 16)
            press = int(request.form['press'], 16)
            direction = int(request.form['direction'], 16)

            button_input = encode_button_input(mode, not_hold, hold, press) 
            result = encode_command_value(button_input, direction)
        except ValueError:
            result = "Invalid hex numbers."

    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    def open_browser():
      webbrowser.open("http://127.0.0.1:5000/")
    threading.Timer(1.0, open_browser).start()
    app.run(debug=False)
