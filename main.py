import discord
import asyncio
import pytesseract
import os
import cv2
import numpy as np
import mss
from dotenv import load_dotenv

pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'  # your path may be different

# Load secrets
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Configure Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Tribe Log Capture Area (tweak this for your screen resolution!)
TRIBE_LOG_REGION = {
    "top": 80,       # Y offset from top of screen
    "left": 1500,    # X offset from left of screen
    "width": 400,    # Width of tribe log area
    "height": 600    # Height of tribe log area
}

# Set for storing previous text
seen_lines = set()

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def capture_tribe_log_text():
    with mss.mss() as sct:
        screenshot = sct.grab(TRIBE_LOG_REGION)
        img = np.array(screenshot)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(gray)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return lines

async def monitor_and_send():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Invalid channel ID or bot lacks permissions.")
        return

    print("🟢 Monitoring started...")

    while not client.is_closed():
        try:
            lines = capture_tribe_log_text()
            new_lines = [line for line in lines if line not in seen_lines]

            for line in new_lines:
                await channel.send(f"📜 **Tribe Log**:\n```\n{line}\n```")
                seen_lines.add(line)

            await asyncio.sleep(5)  # Wait before next check

        except Exception as e:
            print(f"⚠️ Error: {e}")
            await asyncio.sleep(10)

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    client.loop.create_task(monitor_and_send())

client.run(TOKEN)
