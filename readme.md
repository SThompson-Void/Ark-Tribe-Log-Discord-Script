# Ark Tribe Log Discord Script

- Created by mgvoid

## Requirements

- Create a discord bot with default messaging and view channel permissions and generate and grab the token for that bot! <https://discordpy.readthedocs.io/en/stable/discord.html>
- You do not need to do the above if you are MG tribe as mgvoid already made a bot for this
- A discord channel ID (right-click the channel you want to use for discord logs and select "copy channel ID")
- OBS <https://obsproject.com/download> (Used to set your target window to Ark)
- Ark Survival Evolved
- A tribe on your server so you can view your tribelog
- Github CLI to clone this project OR you can download the zip <>
- Python: <https://www.python.org/downloads/>
- Run the command:
  - `pip install python-dotenv && pip install discord && pip install opencv-python && pip install mss && pip install numpy && pip install pytesseract && pip install asyncio`
-Also grab tesseract from here <https://github.com/UB-Mannheim/tesseract/wiki> and check that your path at the beginning of main.py matches your install path for tesseract
-Find tesseract OCR root in your program files and copy that to your environment variable path

## Setup

1. Ensure that you have all above requirements
2. Git clone this project to a directory of your choosing
3. Create a file named `.env`
4. Paste this code into the file and replace your discord bot's token and channel ID respectively

  ``` .env
    DISCORD_TOKEN=your-super-secret-token
    CHANNEL_ID=123456789012345678
  ```

5. Open OBS and set your screen capture window to Ark: Survival Evolved/Ascended
6. Run main.py
7. Go back to Ark and Open the Tribe Log section
8. AFK on the Tribe Log Screen and that's it!
9. To kill the script you can kill it in task manager, close ark, or close OBS!

## How this Script Works / Architecture

OBS (game capture)
      ↓ (displayed content)
Python script (screen capture)
      ↓
OCR processing (Tesseract)
      ↓
Text parsing & filtering
      ↓
Send to Discord via Bot (discord.py)

## Troubleshooting

If your script is not working, check over these:
-you created a file named `.env`
-you pasted the code from step #4 into that `.env` file
-you replaced DISCORD_TOKEN=... in `.env` with your real discord bot's token from requirements section
-you replaced CHANNEL_ID=... in `.env` with the correct channel ID from requirements section
-you have OBS set to target window Ark
-you are ACTUALLY running the script
-you are AFKing with the tribe log window open in Ark
-you did not get kicked from server for AFK, etc.
-you created a discord bot properly and assigned the correct message sending and view channel permissions

## Future Plans

-Integrate anti-afk kick functionality into the script
-Integrate auto-rejoin server functionality into the script to ensure there are no tribe-log downtimes
