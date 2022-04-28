#Title: Hangman
#Author: Richard Gaulke
#
#This game will pull from a pre-built wordlist but a custom wordlist can be imported.
import os
import random
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename

#Global variables
filename = "wordlist.txt"
#This will be a global function to clear the screen
def clear_screen():
    _ = os.system("clear")

#This will be the default pause
def pause():
    PauseProgram = input("Press the <ENTER> key to continue...")

#This creates the start menu
def menu():
    clear_screen()
    title_image = open("hangman_title.txt", "r")
    for line in title_image.readlines():
        print(line)
    print("1) Play Hangman")
    print("2) Quit")
    play = input("Select an option to continue: ")
    if play == "1":
        play_game()
    elif play == "2":
        quit()

#Let's get to the game logic
def play_game():
    clear_screen()
    print("Let's Play Hangman!")
    missed_guesses = ""
    correct_guesses = ""
    misses = 0
    with open(filename, "r") as wordlist:
        all_words = wordlist.read()
        words = list(map(str, all_words.split()))
        word = random.choice(words)
        hidden_word = len(word) * '_'
    while misses <= 6:
        clear_screen()
        with open("miss" + str(misses) + ".txt", "r") as file:
            print(file.read())
        print(hidden_word)
        print("\r\nIncorrect Guesses: " + missed_guesses)
        user_guess = input("\r\nPlease guess a letter: ")
        if user_guess in word:
            correct_guesses = correct_guesses + user_guess
            for i in range(len(word)):
                if word[i] in correct_guesses:
                    hidden_word = hidden_word[:i] + word[i] + hidden_word[i+1:]
        else:
            misses=misses+1
            missed_guesses = missed_guesses + user_guess
        if hidden_word == word:
            title_image = open("hangman_title.txt", "r")
            for line in title_image.readlines():
                print(line)
            misses = 7
            clear_screen()
            print("YOU HAVE WON!!! GREAT JOB!\r\n")
    
    print("Game over the hidden word was " + word + "\r\n")
    pause()
    menu()

#Now we play
while True:
    menu()
