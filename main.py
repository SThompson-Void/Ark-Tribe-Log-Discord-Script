import discord
import asyncio
import pytesseract
import os
import cv2
import numpy as np
import mss
from dotenv import load_dotenv
from difflib import SequenceMatcher

# Path to Tesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# autocorrect functionality via difflib sequencematcher
EXPECTED_WORDS = [
    #lower case
    "turret ", "destroyed ", "structure ", "tribe ", "killed ", "was ", "by ", "tamed ", "your ", "lvl ", "foundation ", "wall ", "tek ", "metal ", "wood ", "thatch ", "stone ", "bag ",
    "your ", "tribe ", "killed ", "bag ", "auto-decay ", "sleeping ", "bag", "triangle",
    #UPPER CASE
    "TURRET", "DESTROYED", "STRUCTURE", "TRIBE", "KILLED", "WAS", "BY", "TAMED", "YOUR", "LVL",
    "FOUNDATION", "WALL", "TEK", "METAL", "WOOD", "THATCH", "STONE", "BAG", "AUTO-DECAY", "SLEEPING", "TRIANGLE",
    #Pascal Case
    "Turret", "Destroyed", "Structure", "Tribe", "Killed", "Was", "By", "Tamed", "Your", "Lvl",
    "Foundation", "Wall", "Tek", "Metal", "Wood", "Thatch", "Stone", "Bag",
    "Auto-Decay", "Sleeping", "Triangle"
]

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def autocorrect_line(line, threshold=0.4):
    words = line.split()
    corrected_words = []

    for word in words:
        best_match = word
        best_score = 0

        for target in EXPECTED_WORDS:
            score = similarity(word.lower(), target)
            if score > best_score:
                best_score = score
                best_match = target

        # Replace if match is above threshold
        if best_score >= threshold:
            corrected_words.append(best_match)
        else:
            corrected_words.append(word)

    return " ".join(corrected_words)


# Track seen lines
seen_lines = set()

# Setup Discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)

def capture_colored_log_lines():
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])  # full primary screen
        img = np.array(screenshot)

        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Red range (split)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([179, 255, 255])
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # Purple range
        lower_purple = np.array([130, 100, 100])
        upper_purple = np.array([155, 255, 255])
        mask_purple = cv2.inRange(hsv, lower_purple, upper_purple)

        # Combine red and purple masks
        mask = cv2.bitwise_or(mask_red, mask_purple)

        # Apply mask to full screenshot
        filtered = cv2.bitwise_and(img, img, mask=mask)

        # Convert to grayscale and threshold
        gray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]

        # OCR
        text = pytesseract.image_to_string(thresh)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return lines

async def monitor_and_send():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Invalid channel ID or bot lacks permissions.")
        return

    print("Monitoring full screen for colored logs...")
    start_token = "Your"
    end_token = "!"

    while not client.is_closed():
        try:
            lines = capture_colored_log_lines()
            new_lines = [line for line in lines if line not in seen_lines]

            i = 0
            while i < len(new_lines):
                line = new_lines[i]

                # If this is the start of a new log group
                if start_token in line:
                    log_block = [line]
                    seen_lines.add(line)
                    i += 1

                    # Collect lines until we hit one that ends with '!'
                    while i < len(new_lines) and end_token not in new_lines[i]:
                        log_block.append(new_lines[i])
                        seen_lines.add(new_lines[i])
                        i += 1

                    # Include the closing line with '!'
                    if i < len(new_lines):
                        log_block.append(new_lines[i])
                        seen_lines.add(new_lines[i])
                        i += 1

                    #now we pass each line through the autocorrect function
                    message = "\n".join(autocorrect_line(line) for line in log_block)
                    await channel.send(f"<@everyone>\n```\n{message}\n```")

                else:
                    # Not part of a known log format; skip or handle individually
                    seen_lines.add(line)
                    i += 1

            await asyncio.sleep(3)

        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

@client.event
async def on_ready():
    print(f" Logged in as {client.user}")
    client.loop.create_task(monitor_and_send())

client.run(TOKEN)
