"""
Fortnite Festival Overdriver by vo-ip9
github: https://github.com/vo-ip9/ff-overdriver
email : 9voip9@gmail.com (feel free to reach out for questions or suggestions)

required files in this directory:
- songs.json
- settings.json

required packages:
- rich
- pygame
- keyboard
- fuzzywuzzy
- prompt_toolkit
"""

import time
import json
import threading
from os import environ
from typing import List, Optional
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # hides the pygame welcome message

import pygame.mixer
from rich.console import Console
from keyboard import press, release, read_event, KEY_DOWN
from fuzzywuzzy import fuzz
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import prompt
console = Console()


class MinLengthValidator(Validator):
    """
    Validator class to ensure input meets a minimum length requirement.
    """
    def __init__(self, min_length: int = 1):
        self.min_length = min_length

    def validate(self, document):
        if len(document.text) < self.min_length:
            raise ValidationError(message=f'input must be at least {self.min_length} character(s)')


class FuzzyWuzzyCompleter(Completer):
    """
    A fuzzy matching completer using the fuzzywuzzy library, suggesting
    completions based on fuzzy matching against a list of words.
    """
    def __init__(self, words, match_threshold=60):
        self.words = words
        self.match_threshold = match_threshold

    def get_completions(self, document, _):
        word = document.text
        if not word:
            for option in self.words:
                yield Completion(option, start_position=0)
            return

        # calculate fuzzy match scores
        matches = []
        for option in self.words:
            ratio = fuzz.ratio(word.lower(), option.lower())
            partial_ratio = fuzz.partial_ratio(word.lower(), option.lower())
            token_sort_ratio = fuzz.token_sort_ratio(word.lower(), option.lower())

            # get the best score out of the three methods
            best_score = max(ratio, partial_ratio, token_sort_ratio)
            if best_score >= self.match_threshold:
                matches.append((best_score, option))

        # sort by highest score and yield completions
        matches.sort(reverse=True)
        for _, option in matches:
            yield Completion(option, start_position=-len(document.text))


def fuzzy_search_autocomplete(autocomplete_words: List[str], prompt_text: str = "Search for a song: ") -> Optional[str]:
    """
    Prompts the user with an autocomplete input using fuzzy matching.
    Returns the selected word or None if cancelled.
    """
    try:
        completer = FuzzyWuzzyCompleter(autocomplete_words)
        result = prompt(
            f"{prompt_text}",
            completer=completer,
            complete_while_typing=True,
            validator=MinLengthValidator(1),
            validate_while_typing=False
        )
        return result.strip() if result else None

    except (KeyboardInterrupt, EOFError):
        console.print("\nsearch cancelled.", style="bold red")
        return None


def press_and_release_key(key, hold_duration):
    """
    Presses and releases a key for a specified duration.
    """
    try:
        press(key)
        time.sleep(hold_duration)
        release(key)
    except Exception as e:
        console.print(f"Error pressing/releasing key '{key}': {e}", style="bold red")


def main():
    """
    Main entry point I guess
    """
    with open("songs.json", "r", encoding="utf-8") as f:
        songs = json.load(f)

    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    except Exception as e:
        console.print(f"Error initializing pygame mixer: {e}", style="bold red")
        return

    # get desired song
    song_names = [song["display_title"] for song in songs]
    selected_song = fuzzy_search_autocomplete(song_names, "Search for a song: ")
    if not selected_song:
        console.print("No song selected. Exiting...", style="bold red")
        return
    song = next(song for song in songs if song["display_title"] == selected_song)

    # get desired instrument
    instruments = ["vocals", "bass", "guitar", "drums", "probass", "proguitar"]
    instrument_index = int(console.input("\n1. Vocals\n2. Bass\n3. Lead\n4. Drums\n5. Pro Bass\n6. Pro Lead\n\nSelect an instrument: ").strip()) - 1
    if instrument_index not in range(len(instruments)):
        console.print("Invalid instrument selection. Exiting...", style="bold red")
        return
    instrument = instruments[instrument_index]

    # get desired difficulty
    difficulties = ["easy", "medium", "hard", "expert"]
    difficulty_index = int(console.input("\n1. Easy\n2. Medium\n3. Hard\n4. Expert\n\nSelect a difficulty: ").strip()) - 1
    if difficulty_index not in range(len(difficulties)):
        console.print("Invalid difficulty selection. Exiting...", style="bold red")
        return
    difficulty = difficulties[difficulty_index]

    # finally, get the timings from the song, instrument, and difficulty
    timings = song["timings"][difficulty][instrument]

    # load settings from settings.json
    delay_ms = settings.get("delay_ms", 0)
    lane_keys = settings.get("lane_keys", ["a", "s", "j", "k", "l"])
    sound_file = settings.get("sound_file", "")
    sound_volume = settings.get("sound_volume", 0.5)
    overdrive_key = settings.get("overdrive_key", "space")
    key_hold_duration = settings.get("key_hold_duration_ms", 50) / 1000  # convert to seconds for sleep function

    # set up the sound player if wanted
    if sound_file:
        sound = pygame.mixer.Sound(sound_file)
        sound.set_volume(sound_volume)
        sound_channel = pygame.mixer.Channel(0)

    # wait for the first key press
    console.print("\nTimer is ready! Tap the first note on time to start.")
    console.print("\nYour lane keys:", style="bold cyan")
    console.print(" ".join(f"\"{k}\"" for k in lane_keys))
    console.print("(Ctrl + C to quit)\n", style="bold cyan ")

    # wait for the first note press
    while True:
        event = read_event()
        if event.event_type == KEY_DOWN and event.name in lane_keys:
            break

    # start the timer
    start_time = time.time()
    played_timings = set()
    console.print(f"Starting overdrive timer for {selected_song} ({instrument})...", style="bold green")

    for timing in timings:
        while (time.time() - start_time) * 1000 < timing - delay_ms:
            time.sleep(0.001) # to pass the time without using too much CPU

        if timing not in played_timings:
            threading.Thread(target=press_and_release_key, args=(overdrive_key, key_hold_duration)).start()
            if sound_file:
                try:
                    if not sound_channel.get_busy():
                        sound_channel.play(sound)
                except Exception as e:
                    console.print(f"Error playing sound: {e}", style="bold red")

            played_timings.add(timing)
            console.log(f"Triggered at {timing} ms")

    # let the last sound play out before ending
    while sound_channel.get_busy():
        time.sleep(0.1)
    console.print("Song overdrives complete.", style="bold cyan")
    time.sleep(100) # exiting immediately can lag the game somewhat, best to wait.


if __name__ == "__main__":
    main()
