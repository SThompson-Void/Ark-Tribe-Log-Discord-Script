import discord
import asyncio
import pytesseract
import os
import cv2
import numpy as np
import mss
from dotenv import load_dotenv

# Path to Tesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

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
        print("❌ Invalid channel ID or bot lacks permissions.")
        return

    print("🟢 Monitoring full screen for colored logs...")

    while not client.is_closed():
        try:
            lines = capture_colored_log_lines()
            new_lines = [line for line in lines if line not in seen_lines]

            for line in new_lines:
                await channel.send(f"📜 **Tribe Log**:\n```\n{line}\n```")
                seen_lines.add(line)

            await asyncio.sleep(5)

        except Exception as e:
            print(f"⚠️ Error: {e}")
            await asyncio.sleep(10)

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    client.loop.create_task(monitor_and_send())

client.run(TOKEN)
