import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from keep_alive import keep_alive
import os

# Set default port for Render if needed
os.environ["PORT"] = "8080"

# Load token from .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Invite data store
invite_data = {}

# Bot setup
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.invites")
        await self.load_extension("cogs.tickets")
        await self.tree.sync()
        print("✅ Slash commands synced.")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')

# Invite count logic
async def get_invite_count(member):
    invites = await member.guild.invites()
    return sum(invite.uses for invite in invites if invite.inviter == member)

# /checkinvites
@bot.tree.command(name="checkinvites", description="Check valid and all-time invites")
async def checkinvites(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    total = await get_invite_count(member)
    valid = total - invite_data.get(member.id, {}).get("reset_total", 0)
    await interaction.response.send_message(
        f"{member.mention}\n✅ Valid Invites: **{valid}**\n📊 All Time Invites: **{total}**"
    )

# /checkinviteeligibility
@bot.tree.command(name="checkinviteeligibility", description="Check if a member can claim rewards")
async def checkinviteeligibility(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    total = await get_invite_count(member)
    valid = total - invite_data.get(member.id, {}).get("reset_total", 0)

    if valid >= 3:
        mod_role = discord.utils.get(interaction.guild.roles, name="Moderator")
        await interaction.response.send_message(
            f"{member.mention} ✅ You are eligible for claiming invite rewards (Valid: **{valid}**)"
        )
        if mod_role:
            await interaction.followup.send(f"{mod_role.mention} 🔔 {member.mention} is eligible to claim.")
    else:
        await interaction.response.send_message(
            f"{member.mention} ❌ You do not have the required number of invites.\n"
            "Kindly invite more people and try again!"
        )

# /inviteclaimcount
@bot.tree.command(name="inviteclaimcount", description="Check how many times a member can claim")
async def inviteclaimcount(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    total = await get_invite_count(member)
    valid = total - invite_data.get(member.id, {}).get("reset_total", 0)
    claims = valid // 3
    await interaction.response.send_message(
        f"{member.mention} 🎁 You can claim **{claims}** time(s) based on **{valid}** valid invites."
    )

# /resetinvites
@bot.tree.command(name="resetinvites", description="Reset invites of a member")
@app_commands.checks.has_any_role("Founder", "Owner", "Moderation Team", "Moderator")
async def resetinvites(interaction: discord.Interaction, member: discord.Member):
    total = await get_invite_count(member)
    invite_data[member.id] = {'reset_total': total}
    await interaction.response.send_message(
        f"🔄 {member.mention}'s invites have been reset.\n"
        f"📊 Old invites are now counted in 'All Time Invites'."
    )

# Error handler for /resetinvites
@resetinvites.error
async def resetinvites_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingAnyRole):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)

# Uptime server
keep_alive()

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)



