# What Is FF Overdriver?
FF Overdriver is a simple script that can overdrive at the best possible times for Fortnite Festival songs. 

# Why?
Optimal usage of overdrive and hitting notes accurately are the most important factors to getting high scores in Fortnite Festival. While the latter can be trained, there is no intuitive way to find the best time to overdrive on most paths/charts. 

Thankfully, people have come up with solutions, notably the "CHOpt" project by GenericMadScientist. While this was made for for Clone Hero, Fortnite Festival is very similar in nature. With some modifications, CHOpt can be used to find optimal overdrive timings for Fortnite Festival paths/charts. This should be useful to anyone wanting to increase their high scores.

This is the underlying algorithm used to find the best timings, and FF Overdriver simply provides a way to make this information actionable.

# Features
- As of Dec 2025, all songs* in Fortnite Festival are supported on all 6 instruments (Vocals, Bass, Lead, Drums, Pro Bass, Pro Lead) and all 4 difficulties (Easy, Medium, Hard, Expert) in the songs.json file, which I update periodically.
- Overdrives for you by pressing the given key and playing a given sound file
- Customizable lane keys, overdrive keys, notification sounds, and more via settings.json
- Easy to start and navigate via a simple GUI
- Easy searching of songs and instrument with fuzzy searching
- Album art is supported in the song selection screen

*i by Kendrick Lamar is the only song not supported

# Installation
1. First, make sure you have Python installed. I recommed Python 3.12, as some of the packages may not support newer versions.
2. Clone this repository or download the latest release .zip (version 2.0)
```
git clone https://github.com/vo-ip9/ff-overdriver
```
3. Look through the `settings.json` file and change the lane keys and overdrive key to what you would like or what you have in-game. 
4. Install the requirements and run the main file.
```
pip install -r requirements.txt
```
```
python main.py
```
# Usage
After running the main file, the GUI should open. From there, you can type the song you would like and select the instrument and difficulty. Once ready, press the select song button, switch to the game application and start playing the song. Make sure that you don't click any of your lane keys until you press the first note, otherwise the timings will be too early. The timer's accuracy relies entirely on how accurately you play the first note. If it's not a 'perfect' note, I would recommend restarting it.

# Results
While using these timings, I can quite consistently get within the top 50 leaderboard places, and have even got some first, second and third places, but this is only half the equation. You need to hit every note, and have a fairly high (>90%) accuracy to get high placements, even with perfect overdrives. I have no doubt that if you have an even higher accuracy, you can get first place on some songs using these timings.

If you have any questions or suggestions, feel free to email me at 9voip9@gmail.com. Good luck!
