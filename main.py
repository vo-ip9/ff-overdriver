"""
Fortnite Festival Overdriver by vo-ip9
github: https://github.com/vo-ip9/ff-overdriver
email : 9voip9@gmail.com (feel free to reach out for questions or suggestions)

required files in this directory:
- songs.json
- settings.json

required packages:
- customtkinter
- requests
- pygame
- rapidfuzz
- pynput
- pillow
"""

import time
import json
import threading
from io import BytesIO
import requests
import customtkinter as ctk
import pygame.mixer
from rapidfuzz import process, fuzz
from pynput import keyboard
from PIL import Image


with open("songs.json", "r", encoding="utf-8") as f:
    SONGS = json.load(f)
DISPLAY_TITLES = [s["display_title"] for s in SONGS]

with open("settings.json", "r", encoding="utf-8") as f:
    SETTINGS = json.load(f)

INSTURMENT_MAP = {"Vocals": "vocals", "Bass": "bass", "Lead": "guitar", "Drums": "drums", 
                  "Pro Bass": "probass", "Pro Lead": "proguitar"}


class SongSelectionGUI(ctk.CTk):
    """Main GUI class for song selection and timer control."""
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Rhythm Game Song Select")
        self.geometry("700x660")
        self.resizable(False, False)

        # variables
        self.selected_song = None
        self.instrument_var = ctk.StringVar(value="Vocals")
        self.difficulty_var = ctk.StringVar(value="Expert")
        self.search_var = ctk.StringVar()

        # timing variables
        self.timer_running = False
        self.timer_thread = None
        self.keyboard_listener = None
        self.lane_keys_pressed = set()

        # initialize pygame mixer
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.sound = None
            self.sound_channel = None
            if SETTINGS.get("sound_file", ""):
                self.sound = pygame.mixer.Sound(SETTINGS["sound_file"])
                self.sound.set_volume(SETTINGS.get("sound_volume", 0.5))
                self.sound_channel = pygame.mixer.Channel(0)
        except Exception as e:
            print(f"Error initializing pygame mixer: {e}")
            self.sound = None

        # layout frames
        self.grid_columnconfigure(1, weight=1)

        self.left_frame = ctk.CTkFrame(self, width=350)
        self.left_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.build_left_panel()
        self.build_right_panel()

        # start keyboard listener
        self.start_keyboard_listener()

    # -------------------------------------------------
    # left panel
    # -------------------------------------------------
    def build_left_panel(self):
        """Build the left panel with search and instrument/difficulty options."""
        # search entry
        self.search_entry = ctk.CTkEntry(
            self.left_frame,
            width=260,
            placeholder_text="Search for a song...",
            placeholder_text_color="#808080",
        )
        self.search_entry.pack(anchor="w", padx=20, pady=(20, 0))
        self.search_entry.bind("<KeyRelease>", self.update_search_results)

        # results box
        self.results_frame = ctk.CTkScrollableFrame(
            self.left_frame,
            width=240,
            height=150,
            fg_color=("#1d1d1d", "#1d1d1d")
        )
        self.results_frame.pack(anchor="w", pady=10, padx=20)

        # instrument buttons
        ctk.CTkLabel(self.left_frame, text="Instrument", font=("Arial", 16)).pack(
            anchor="w", padx=20, pady=5)

        for inst in ["Vocals", "Bass", "Lead", "Drums", "Pro Bass", "Pro Lead"]:
            ctk.CTkRadioButton(
                self.left_frame,
                text=inst,
                variable=self.instrument_var,
                value=inst,
                command=self.update_right_panel,
                radiobutton_width=14,
                radiobutton_height=14
            ).pack(anchor="w", padx=20)

        # difficulty buttons
        ctk.CTkLabel(self.left_frame, text="Difficulty", font=("Arial", 16)).pack(
            anchor="w", padx=20, pady=(20, 5))

        for diff in ["Easy", "Medium", "Hard", "Expert"]:
            ctk.CTkRadioButton(
                self.left_frame,
                text=diff,
                variable=self.difficulty_var,
                value=diff,
                command=self.update_right_panel,
                radiobutton_height=14,
                radiobutton_width=14
            ).pack(anchor="w", padx=20)
        ctk.CTkLabel(self.left_frame, text="", height=20).pack(anchor="w", pady=10) # spacer


    # -------------------------------------------------
    # right panel
    # -------------------------------------------------
    def build_right_panel(self):
        """Build the right panel with song info and start button."""
        self.cover_frame = ctk.CTkFrame(self.right_frame, width=320, height=320, fg_color="black")
        self.cover_frame.pack(padx=20, pady=20)
        self.cover_frame.pack_propagate(False)

        img = Image.new("RGB", (320, 320), color="black")
        self.default_cover_img = ctk.CTkImage(light_image=img, dark_image=img, size=(320, 320))

        self.cover_label = ctk.CTkLabel(self.cover_frame, image=self.default_cover_img, text="")
        self.cover_label.place(relx=0.5, rely=0.5, anchor="center")

        self.loading_label = ctk.CTkLabel(self.right_frame, text="", font=("Arial", 24), fg_color="transparent")
        self.loading_label.place_forget()  # hide initially

        self.title_label = ctk.CTkLabel(self.right_frame, text="---", font=("Arial", 20, "bold"))
        self.artist_label = ctk.CTkLabel(self.right_frame, text="---", font=("Arial", 16))
        self.duration_label = ctk.CTkLabel(self.right_frame, text="---", font=("Arial", 16)) 
        self.instrument_and_difficulty_label = ctk.CTkLabel(self.right_frame, text="---", font=("Arial", 16))
        self.timings_label = ctk.CTkLabel(self.right_frame, text="---", font=("Arial", 16))
        self.start_button = ctk.CTkButton(self.right_frame, text="Confirm Song", width=100, command=self.start_song)
        self.info_label = ctk.CTkLabel(self.right_frame, text="---", font=("Arial", 16), text_color="#1f6aa5")

        self.title_label.pack(anchor="w", padx=20)
        self.artist_label.pack(anchor="w", padx=20)
        self.duration_label.pack(anchor="w", padx=20, pady=(0, 20))
        self.instrument_and_difficulty_label.pack(anchor="w", padx=20)
        self.timings_label.pack(anchor="w", padx=20)
        self.start_button.pack(pady=15)
        self.info_label.pack(side="top")


    # -------------------------------------------------
    # rapidfuzz search
    # -------------------------------------------------
    def update_search_results(self, event=None):
        """Update search results based on the search entry."""
        # clear all old items before next search term
        for child in self.results_frame.winfo_children():
            child.destroy()

        query = self.search_entry.get().strip().lower() # sanitize the search
        if not query:
            return

        # map the lowercase titles to original (display) titles
        title_map = {t.lower(): t for t in DISPLAY_TITLES}
        lower_titles = list(title_map.keys())

        results = process.extract(query, lower_titles, scorer=fuzz.WRatio, limit=10)
        titles = [title_map[r[0]] for r in results]  # get original casing

        for title in titles:
            self.add_result_row(title)


    # -------------------------------------------------
    # add a row for each result
    # -------------------------------------------------
    def add_result_row(self, title):
        """Add a clickable row for a search result."""
        row = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        row.pack(fill="x")

        label = ctk.CTkLabel(
            row,
            text=title,
            anchor="w",
            width=260,
            fg_color="transparent",
        )
        label.pack(fill="x", padx=5)
        label.bind("<Button-1>", lambda _, t=title: self.select_song(t))
        row.bind("<Button-1>", lambda _, t=title: self.select_song(t))


    # -------------------------------------------------
    # song selection
    # -------------------------------------------------
    def select_song(self, title):
        """Handle song selection from search results."""
        self.search_var.set("")  # clear search
        for c in self.results_frame.winfo_children():
            c.destroy()

        for s in SONGS:
            if s["display_title"] == title:
                self.selected_song = s
                break
        
        self.update_right_panel()


    # -------------------------------------------------
    # update right panel with song info
    # -------------------------------------------------
    def update_right_panel(self):
        """Update the right panel with selected song info."""
        if self.selected_song:
            dn_min, dn_sec = divmod(int(self.selected_song['duration']), 60)
            timings = self.selected_song['timings'][self.difficulty_var.get().lower()][INSTURMENT_MAP[self.instrument_var.get()]]

            self.title_label.configure(text=self.selected_song['display_title'])
            self.artist_label.configure(text=self.selected_song['artist_name'])
            self.duration_label.configure(text=f"{dn_min}:{dn_sec:02d}")
            self.timings_label.configure(text=f"{len(timings)} overdrive timing(s)")

            # set album art to default while loading
            self.cover_label.configure(image=self.default_cover_img)
            self.cover_label.image = self.default_cover_img

            self.start_loading_animation()
            threading.Thread(
                target=self.load_album_art_async,
                daemon=True
            ).start()
        self.instrument_and_difficulty_label.configure(text=
            f"{self.instrument_var.get().title()}  ♫  {self.difficulty_var.get().title()}")


    def update_album_art(self, ctk_image):
        """Update the album art image in the UI."""
        self.cover_label.configure(image=ctk_image)
        self.cover_label.image = ctk_image
        self.stop_loading_animation()


    def load_album_art_async(self):
        """Load album art image asynchronously."""
        try:
            response = requests.get(self.selected_song['album_art_url'], timeout=5)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            pil_image = Image.open(img_data).convert("RGB")
            pil_image = pil_image.resize((320, 320), Image.LANCZOS)

            # PIL -> CTkImage
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(320, 320))

            # update UI from the main thread
            self.after(0, lambda: self.update_album_art(ctk_image))

        except Exception as e:
            print("Error loading album art:", e)
            self.after(0, self.stop_loading_animation)


    def start_loading_animation(self):
        """Start the loading animation."""
        self.loading_running = True
        self.loading_frames = ["Loading   ", "Loading.  ", "Loading.. ", "Loading..."]
        self.loading_index = 0
        self.animate_loading()


    def animate_loading(self):
        """Animate the loading label."""
        if not self.loading_running:
            return

        frame = self.loading_frames[self.loading_index]
        self.loading_label.configure(text=frame)
        self.loading_label.place(relx=0.5, rely=0.3, anchor="center")
        self.loading_index = (self.loading_index + 1) % len(self.loading_frames)
        self.after(200, self.animate_loading)


    def stop_loading_animation(self):
        """Stop the loading animation."""
        self.loading_running = False
        self.loading_label.place_forget()


    # -------------------------------------------------
    # keyboard listener
    # -------------------------------------------------
    def start_keyboard_listener(self):
        """Start the keyboard listener for lane key presses."""
        def on_press(key):
            try:
                key_char = key.char
            except AttributeError:
                key_char = str(key).replace("Key.", "")

            lane_keys = SETTINGS.get("lane_keys", ["a", "s", "j", "k", "l"])
            if key_char in lane_keys and not self.timer_running:
                self.lane_keys_pressed.add(key_char)

                # start timer if waiting
                if hasattr(self, 'waiting_for_start') and self.waiting_for_start:
                    self.waiting_for_start = False
                    self.start_timing_thread()

        def on_release(key):
            try:
                key_char = key.char
            except AttributeError:
                key_char = str(key).replace("Key.", "")

            if key_char in self.lane_keys_pressed:
                self.lane_keys_pressed.discard(key_char)

        self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.keyboard_listener.start()


    # -------------------------------------------------
    # start song timer
    # -------------------------------------------------
    def start_song(self):
        """Start the song timer after confirming selection."""
        if not self.selected_song:
            self.info_label.configure(text="No song selected!")
            return

        if self.timer_running:
            self.info_label.configure(text="Timer already running!")
            return

        lane_keys = SETTINGS.get("lane_keys", ["a", "s", "j", "k", "l"])
        self.info_label.configure(text=
            f"Timer ready! Press any lane key to start:\n{' '.join(lane_keys)}")
        self.waiting_for_start = True


    def start_timing_thread(self):
        """Start the timing thread to handle overdrive triggering."""
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()


    def run_timer(self):
        """Run the timer to trigger overdrive at specified timings."""
        instrument = INSTURMENT_MAP[self.instrument_var.get()]
        difficulty = self.difficulty_var.get().lower()
        timings = self.selected_song['timings'][difficulty][instrument]

        delay_ms = SETTINGS.get("delay_ms", 0)
        overdrive_key = SETTINGS.get("overdrive_key", "space")
        key_hold_duration = SETTINGS.get("key_hold_duration_ms", 50) / 1000

        # update the UI
        self.after(0, lambda: self.info_label.configure(text="Timer started!"))

        # start the timer
        start_time = time.time()
        played_timings = set()

        for timing in timings:
            if not self.timer_running:
                break

            # wait until the right time
            while (time.time() - start_time) * 1000 < timing - delay_ms:
                if not self.timer_running:
                    break
                time.sleep(0.001)

            if not self.timer_running:
                break

            if timing not in played_timings:
                # press and release overdrive key
                threading.Thread(
                    target=self.press_and_release_key, 
                    args=(overdrive_key, key_hold_duration),
                    daemon=True
                ).start()

                # play sound if channel is not busy
                if self.sound and self.sound_channel:
                    try:
                        if not self.sound_channel.get_busy():
                            self.sound_channel.play(self.sound)
                    except Exception as e:
                        print(f"Error playing sound: {e}")

                played_timings.add(timing)
                elapsed = (time.time() - start_time) * 1000
                self.after(0, lambda t=timing, e=elapsed: self.update_timing_info(t, e))

        # wait for the last sound to end before finishing 
        if self.sound_channel:
            while self.sound_channel.get_busy():
                time.sleep(0.1)

        self.timer_running = False
        self.after(0, lambda: self.info_label.configure(text="Song complete! Select another song."))


    def update_timing_info(self, timing, elapsed):
        """Update the timing info label in the UI."""
        self.info_label.configure(text=
            f"Overdrive triggered at {int(elapsed)} ms\n(Target: {timing} ms)")



    def press_and_release_key(self, key, hold_duration):
        """Press and release a key using pynput."""
        controller = keyboard.Controller()
        try:
            # handle special keys
            if key == "space":
                key_obj = keyboard.Key.space
            elif key == "shift":
                key_obj = keyboard.Key.shift
            elif key == "ctrl":
                key_obj = keyboard.Key.ctrl
            elif key == "alt":
                key_obj = keyboard.Key.alt
            else:
                key_obj = key

            # press and release
            controller.press(key_obj)
            time.sleep(hold_duration)
            controller.release(key_obj)

        except Exception as e:
            print(f"Error pressing/releasing key '{key}': {e}")


    def on_closing(self):
        """Handle GUI closing event."""
        self.timer_running = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        self.destroy()


# -------------------------------------------------
# run the GUI
# -------------------------------------------------
if __name__ == "__main__":
    gui = SongSelectionGUI()
    gui.protocol("WM_DELETE_WINDOW", gui.on_closing)
    gui.mainloop()
