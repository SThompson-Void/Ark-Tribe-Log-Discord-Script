from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

print(f"Sending to channel {CHANNEL_ID} with token length {len(DISCORD_TOKEN)}")
