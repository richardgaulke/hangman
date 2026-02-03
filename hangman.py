# Title: Hangman
# Author: Richard Gaulke
#
# This game will pull from a pre-built wordlist but a custom wordlist can be imported.
import os
import random
import secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for

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

WORDLIST_FILENAME = "wordlist.txt"
MISS_FILES = [f"miss{i}.txt" for i in range(7)]


def load_words(filename: str) -> list[str]:
    with open(filename, "r") as wordlist:
        all_words = wordlist.read()
    return list(map(str, all_words.split()))


def load_miss_art() -> list[str]:
    art = []
    for file_name in MISS_FILES:
        with open(file_name, "r") as file:
            art.append(file.read())
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

    @app.route("/", methods=["GET"])
    def index() -> str:
        if "word" not in session:
            new_game()
        return render_template(
            "index.html",
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

        if guess_value in session.get("correct_guesses", []) or guess_value in session.get(
            "missed_guesses", []
        ):
            session["status_message"] = "You already guessed that letter."
            return redirect(url_for("index"))

        if guess_value in session.get("word", ""):
            session["correct_guesses"].append(guess_value)
            update_hidden_word(guess_value)
            session["status_message"] = "Nice guess!"
        else:
            session["misses"] = session.get("misses", 0) + 1
            session["missed_guesses"].append(guess_value)
            session["status_message"] = "Incorrect guess."

        if "_" not in session.get("hidden_word", []):
            flash(f"YOU HAVE WON!!! GREAT JOB! The word was {session.get('word', '')}.")
            new_game()
        elif session.get("misses", 0) >= len(miss_art) - 1:
            flash(f"Game over! The hidden word was {session.get('word', '')}.")
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
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
