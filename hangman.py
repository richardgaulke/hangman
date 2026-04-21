import os
import random
import secrets

import requests
from flask import Flask, flash, get_flashed_messages, redirect, render_template_string, request, session, url_for


TITLE_ART = (
    " _   _                  ___  ___            \n"
    "| | | |                 |  \\/  |            \n"
    "| |_| | __ _ _ __   __ _| .  . | __ _ _ __  \n"
    "|  _  |/ _` | '_ \\ / _` | |\\/| |/ _` | '_ \\ \n"
    "| | | | (_| | | | | (_| | |  | | (_| | | | |\n"
    "\\_| |_/\\__,_|_| |_|\\__, \\_|  |_/\\__,_|_| |_|\n"
    "                    __/ |                   \n"
    "                   |___/                    \n"
)

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Hangman</title>
  <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: #090b10;
      color: #c8d6e5;
      font-family: 'Share Tech Mono', monospace;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1rem;
      background-image:
        linear-gradient(rgba(0,255,180,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,180,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
    }

    .title-wrap {
      border: 1px solid #00ffb422;
      border-radius: 8px;
      padding: 1rem 2rem;
      margin-bottom: 2rem;
      background: #0d1117;
      box-shadow: 0 0 30px #00ffb408;
    }

    pre.title-art {
      font-size: 0.7rem;
      color: #00ffb4;
      line-height: 1.3;
      text-shadow: 0 0 8px #00ffb466;
    }

    .title-subtext {
      margin-top: 0.75rem;
      text-align: center;
      font-size: 0.65rem;
      color: #7f8fa6;
      letter-spacing: 0.08em;
      text-shadow: 0 0 6px #00ffb422;
    }

    .game-grid {
      display: grid;
      grid-template-columns: minmax(320px, 1fr) max-content;
      gap: 1.5rem;
      width: fit-content;
      max-width: 100%;
      margin: 0 auto;
      align-items: start;
    }

    .word-panel {
      width: max-content;
      min-width: 320px;
    }

    .panel {
      background: #0d1117;
      border: 1px solid #00ffb422;
      border-radius: 8px;
      padding: 1.5rem;
      position: relative;
    }

    .panel-label {
      font-family: 'Orbitron', sans-serif;
      font-size: 0.6rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: #00ffb4;
      margin-bottom: 1rem;
      opacity: 0.7;
    }

    pre.miss-art {
      font-size: 1rem;
      color: #e05a5a;
      line-height: 1.4;
      text-shadow: 0 0 6px #e05a5a44;
      min-height: 9rem;
    }

    .hidden-word {
      font-family: 'Orbitron', sans-serif;
      font-size: 2rem;
      letter-spacing: 0.6rem;
      color: #00ffb4;
      text-shadow: 0 0 12px #00ffb466;
      margin: 1rem 0;
      white-space: nowrap;
      word-break: normal;
      overflow-wrap: normal;
    }

    .status {
      font-size: 0.85rem;
      color: #7f8fa6;
      margin-bottom: 1rem;
      min-height: 1.2rem;
    }

    .missed-label {
      font-size: 0.7rem;
      color: #7f8fa6;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 0.4rem;
    }

    .missed-letters {
      font-size: 1rem;
      color: #e05a5a;
      letter-spacing: 0.2rem;
      text-shadow: 0 0 6px #e05a5a44;
      min-height: 1.4rem;
    }

    .guess-form {
      display: flex;
      gap: 0.5rem;
      margin-top: 1.5rem;
      align-items: center;
    }

    input[type=text] {
      font-family: 'Orbitron', sans-serif;
      font-size: 1.2rem;
      width: 3rem;
      text-align: center;
      background: #090b10;
      color: #00ffb4;
      border: 1px solid #00ffb444;
      border-radius: 4px;
      padding: 0.4rem;
      outline: none;
      text-transform: uppercase;
    }

    input[type=text]:focus {
      border-color: #00ffb4;
      box-shadow: 0 0 8px #00ffb433;
    }

    button {
      font-family: 'Orbitron', sans-serif;
      font-size: 0.7rem;
      letter-spacing: 0.1em;
      padding: 0.5rem 1.2rem;
      background: transparent;
      color: #00ffb4;
      border: 1px solid #00ffb444;
      border-radius: 4px;
      cursor: pointer;
      text-transform: uppercase;
      transition: background 0.2s, box-shadow 0.2s;
    }

    button:hover {
      background: #00ffb411;
      box-shadow: 0 0 10px #00ffb422;
    }

    button.danger {
      color: #e05a5a;
      border-color: #e05a5a44;
    }

    button.danger:hover {
      background: #e05a5a11;
      box-shadow: 0 0 10px #e05a5a22;
    }

    .flash {
      font-family: 'Orbitron', sans-serif;
      font-size: 0.85rem;
      color: #f1c40f;
      text-shadow: 0 0 8px #f1c40f55;
      letter-spacing: 0.05em;
      padding: 0.75rem 1rem;
      border: 1px solid #f1c40f33;
      border-radius: 6px;
      background: #f1c40f08;
      margin-bottom: 1.5rem;
      max-width: 860px;
      width: 100%;
      text-align: center;
    }

    .corner {
      position: absolute;
      width: 8px;
      height: 8px;
      border-color: #00ffb4;
      border-style: solid;
      opacity: 0.4;
    }
    .corner.tl { top: 6px; left: 6px; border-width: 1px 0 0 1px; }
    .corner.tr { top: 6px; right: 6px; border-width: 1px 1px 0 0; }
    .corner.bl { bottom: 6px; left: 6px; border-width: 0 0 1px 1px; }
    .corner.br { bottom: 6px; right: 6px; border-width: 0 1px 1px 0; }

    #result-image {
      display: none;
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 3in;
      height: 3in;
      object-fit: contain;
      opacity: 0;
      transition: opacity 2s ease;
      z-index: 999;
      border-radius: 8px;
      box-shadow: 0 0 60px #00000088;
    }
  </style>
</head>
<body>

  <div class="title-wrap">
    <pre class="title-art">{{ title_art }}</pre>
    <div class="title-subtext">Scoreboard is located on port 5002.</div>
  </div>

  {% set messages = get_flashed_messages() %}
  {% if messages %}
    {% for message in messages %}
      <div class="flash">{{ message }}</div>
      {% if "WON" in message %}
        <img id="result-image" src="/static/win.jpg">
      {% else %}
        <img id="result-image" src="/static/lose.gif">
      {% endif %}
    {% endfor %}
  {% endif %}

  <div class="game-grid">
    <div class="panel">
      <div class="corner tl"></div><div class="corner tr"></div>
      <div class="corner bl"></div><div class="corner br"></div>
      <div class="panel-label">Gallows</div>
      <pre class="miss-art">{{ miss_art }}</pre>
    </div>

    <div class="panel word-panel">
      <div class="corner tl"></div><div class="corner tr"></div>
      <div class="corner bl"></div><div class="corner br"></div>
      <div class="panel-label">Word</div>
      <div class="hidden-word">{{ hidden_word | join(' ') }}</div>
      <p class="status">{{ status_message }}</p>
      <div class="missed-label">Missed</div>
      <div class="missed-letters">{{ missed_guesses | join('  ') or '—' }}</div>

      {% if not game_over %}
      <form method="POST" action="/guess" class="guess-form">
        <input type="text" name="guess" maxlength="1" autofocus/>
        <button type="submit">Guess</button>
      </form>
      {% endif %}

      <form method="POST" action="/new-game" style="margin-top: 1rem;">
        <button type="submit" class="danger">New Game</button>
      </form>
    </div>
  </div>

  <script>
    const img = document.getElementById('result-image');
    if (img) {
      img.style.display = 'block';
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          img.style.opacity = '1';
          setTimeout(() => {
            img.style.opacity = '0';
            setTimeout(() => img.style.display = 'none', 2000);
          }, 2000);
        });
      });
    }
  </script>
</body>
</html>"""

WORDLIST_FILENAME = "wordlist.txt"
MISS_FILES = [f"miss{i}.txt" for i in range(7)]

def load_words(filename: str) -> list[str]:
    try:
        with open(filename, "r") as wordlist:
            return wordlist.read().split()
    except FileNotFoundError:
        raise FileNotFoundError(f"Wordlist file '{filename}' not found.")
    except OSError as e:
        raise OSError(f"Could not read wordlist file '{filename}': {e}")


def load_miss_art() -> list[str]:
    art = []
    for file_name in MISS_FILES:
        try:
            with open(file_name, "r") as file:
                art.append(file.read())
        except FileNotFoundError:
            raise FileNotFoundError(f"Miss art file '{file_name}' not found.")
        except OSError as e:
            raise OSError(f"Could not read miss art file '{file_name}': {e}")
    return art


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("HANGMAN_SECRET_KEY", secrets.token_hex(16))



    words = load_words(WORDLIST_FILENAME)
    miss_art = load_miss_art()

    def new_game() -> None:
        word = random.choice(words)
        session["word"] = word
        session["hidden_word"] = ["_" for _ in word]
        session["missed_guesses"] = []
        session["correct_guesses"] = []
        session["misses"] = 0

    def update_hidden_word(guess: str) -> None:
        hidden_word = session.get("hidden_word", [])
        word = session.get("word", "")
        for index, letter in enumerate(word):
            if letter == guess:
                hidden_word[index] = letter
        session["hidden_word"] = hidden_word

    def is_game_over() -> bool:
        return session.get("misses", 0) >= len(miss_art) - 1 or "_" not in session.get(
            "hidden_word", []
        )

    def post_score(result: str, word: str) -> None:
        try:
            requests.post(
                "http://localhost:5002/event",
                json={"result": result, "word": word},
                timeout=1,
            )
        except requests.RequestException:
            pass

    @app.route("/", methods=["GET"])
    def index() -> str:
        if "word" not in session:
            new_game()
        return render_template_string(
            TEMPLATE,
            title_art=TITLE_ART,
            miss_art=miss_art[session.get("misses", 0)],
            hidden_word=session.get("hidden_word", []),
            missed_guesses=session.get("missed_guesses", []),
            status_message=session.get("status_message", "Let's play Hangman!"),
            game_over=is_game_over(),
        )

    @app.route("/guess", methods=["POST"])
    def guess() -> str:
        if "word" not in session:
            new_game()

        guess_value = request.form.get("guess", "").strip().lower()

        if not guess_value:
            session["status_message"] = "Enter a letter to guess."
            return redirect(url_for("index"))

        if len(guess_value) != 1 or not guess_value.isalpha():
            session["status_message"] = "Please enter a single letter."
            return redirect(url_for("index"))

        word = session["word"]
        misses = session["misses"]
        correct_guesses = session["correct_guesses"]
        missed_guesses = session["missed_guesses"]
        hidden_word = session["hidden_word"]

        if guess_value in correct_guesses or guess_value in missed_guesses:
            session["status_message"] = "You already guessed that letter."
            return redirect(url_for("index"))

        if guess_value in word:
            correct_guesses.append(guess_value)
            for i, letter in enumerate(word):
                if letter == guess_value:
                    hidden_word[i] = letter
            session["correct_guesses"] = correct_guesses
            session["hidden_word"] = hidden_word
            session["status_message"] = "Nice guess!"
        else:
            misses += 1
            missed_guesses.append(guess_value)
            session["misses"] = misses
            session["missed_guesses"] = missed_guesses
            session["status_message"] = "Incorrect guess."

        if "_" not in hidden_word:
            flash(f"YOU HAVE WON!!! GREAT JOB! The word was {word}.")
            post_score("win", word)
            new_game()
        elif session["misses"] >= len(miss_art) - 1:
            flash(f"Game over! The hidden word was {word}.")
            post_score("loss", word)
            new_game()

        return redirect(url_for("index"))

    @app.route("/new-game", methods=["POST"])
    def reset_game() -> str:
        new_game()
        session["status_message"] = "New game started!"
        return redirect(url_for("index"))

    return app


def main() -> None:
    if not os.path.exists(WORDLIST_FILENAME):
        raise FileNotFoundError(f"Missing {WORDLIST_FILENAME} in current directory.")

    app = create_app()
    app.run(host="0.0.0.0", port=80, debug=False)


if __name__ == "__main__":
    main()
