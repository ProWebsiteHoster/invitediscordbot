import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

# Set up port for Render
os.environ["PORT"] = "8080"

# Load .env for token
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Custom bot class
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.invites")
        await self.load_extension("cogs.tickets")
        await self.tree.sync()
        print("✅ Slash commands synced.")

# Initialize bot
bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

# Keep-alive server for uptime monitoring
keep_alive()

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)


