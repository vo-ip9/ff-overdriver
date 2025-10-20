# What Is FF Overdriver?
FF Overdriver is a simple script that can overdrive (or simply indicate when to) at the best possible times during Fortnite Festival songs. 

# Why?
Optimal usage of overdrive and hitting notes accurately are the most important factors to getting high scores in Fortnite Festival. While the latter can be trained, there is no intuitive way to find the best time to overdrive on most paths/charts. 

Thankfully, people have come up with solutions, notably the "CHOpt" project by GenericMadScientist. While this was made for for Clone Hero, Fortnite Festival is very similar in nature. With some modifications, CHOpt can be used to find optimal overdrive timings for Fortnite Festival paths/charts. This should be useful to anyone wanting to increase their high scores.

This is the underlying algorithm used to find the best timings, and FF Overdriver simply provides a way to make this information actionable.

# Features
- As of Oct 2025, all songs* in Fortnite Festival are supported on all 6 instruments (Vocals, Bass, Lead, Drums, Pro Bass, Pro Lead) in the songs.json file, which I will update periodically.
- Overdrives for you by pressing the given key or simply notifies you by playing a given sound file (or both!)
- Customizable keybinds, overdrive keys, notification sounds, and more via settings.json
- Easy to start and navigate via a simple command line interface
- Easy searching of songs and instrument with fuzzy searching

*i by Kendrick Lamar is the only song not supported

# Installation
1. First, make sure you have Python installed. Any Python3 version should work.
2. Clone this repository or download the latest release .zip (version 1.0)
```
git clone https://github.com/vo-ip9/ff-overdriver
```
3. I would recommend looking through the `settings.json` file and changing the lane keys and overdrive key to what you would like or what you have in-game. 
4. Install the requirements and run the main file (keep this terminal open, it will be where you choose the song and instrument etc.)
```
pip install -r requirements.txt
```
```
python main.py
```
# Usage
After running the main file, you can type the song you would like and select it using the arrow keys and Enter. Then choose the number cooresponding to your instrument. Finally, switch to the game application and start playing the song. Make sure that you don't click any of your lane keys until you press the first note, otherwise the timings will be early. The timer's accuracy relies entirely on how accurately you play the first note. If it's not a 'perfect', I would recommend restarting it.

# Results
While using these timings, I have learned many songs and can quite consistently get within the top 50 leaderboard places, and have even got some 2s and 3s, but this is only half the equation. You most definetly need to be hitting every note, and have a fairly high (>85%) accuracy to get high placements, even with perfect overdrives. I have no doubt that if you have an even higher accuracy, you could get #1 on some songs using these timings.

If you have any questions or suggestions, feel free to email me at 9voip9@gmail.com. Good luck!
