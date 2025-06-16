import discord
from discord.ext import commands
import asyncio
import json
import os
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "invite_data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def get_invite_count(member):
    invites = await member.guild.invites()
    total = 0
    for invite in invites:
        if invite.inviter == member:
            total += invite.uses
    return total

def get_user_data(user_id):
    data = load_data()
    return data.get(str(user_id), {"all_time": 0, "valid": 0})

def set_user_data(user_id, all_time, valid):
    data = load_data()
    data[str(user_id)] = {"all_time": all_time, "valid": valid}
    save_data(data)

@bot.event
async def on_ready():
    print(f"✅ Bot is ready as {bot.user}")

@bot.command(name="checkinvites")
async def check_invites(ctx, member: discord.Member = None):
    member = member or ctx.author
    current = await get_invite_count(member)
    saved = get_user_data(member.id)
    valid = current - (saved["all_time"] - saved["valid"])
    await ctx.send(f"{member.mention} has:\n🔹 Valid Invites: {valid}\n🔹 All-Time Invites: {current}")

@bot.command(name="checkinviteeligibility")
async def check_eligibility(ctx, member: discord.Member = None):
    member = member or ctx.author
    current = await get_invite_count(member)
    saved = get_user_data(member.id)
    valid = current - (saved["all_time"] - saved["valid"])
    if valid >= 3:
        await ctx.send(f"{member.mention} ✅ You are eligible to claim rewards!")
        mod_role = discord.utils.get(ctx.guild.roles, name="Moderator")
        if mod_role:
            await ctx.send(f"{mod_role.mention} {member.mention} is eligible to claim.")
    else:
        await ctx.send(f"{member.mention} ❌ You need at least 3 invites to claim. Keep inviting!")

@bot.command(name="inviteclaimcount")
async def invite_claim_count(ctx, member: discord.Member = None):
    member = member or ctx.author
    current = await get_invite_count(member)
    saved = get_user_data(member.id)
    valid = current - (saved["all_time"] - saved["valid"])
    count = valid // 3
    await ctx.send(f"{member.mention} can claim {count} time(s) based on {valid} valid invites.")

@bot.command(name="resetinvites")
async def reset_invites(ctx, member: discord.Member):
    allowed_roles = ["Founder", "Owner", "Moderation Team", "Moderator"]
    if not any(role.name in allowed_roles for role in ctx.author.roles):
        return await ctx.send("❌ You don’t have permission to reset invites.")

    current = await get_invite_count(member)
    saved = get_user_data(member.id)
    set_user_data(member.id, current, 0)
    await ctx.send(f"{member.mention}'s invites have been reset. All-time count saved!")

# ===== Ticket System =====

TICKET_CATEGORY_NAME = "🎫 Tickets"

@bot.command(name="ticket")
async def ticket(ctx):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
    if not category:
        category = await guild.create_category(TICKET_CATEGORY_NAME)
    
    ticket_channel = await guild.create_text_channel(
        f"ticket-{ctx.author.name}",
        category=category,
        overwrites={
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
    )
    await ticket_channel.send(f"{ctx.author.mention} Your ticket has been created. A moderator will assist you soon.")

@bot.command(name="closeticket")
async def close_ticket(ctx):
    if "ticket" in ctx.channel.name:
        await ctx.send("Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        await ctx.channel.delete()

# ===== Render Web Server (for uptime) =====

async def handle(request):
    return web.Response(text="Bot is alive!")

app = web.Application()
app.router.add_get("/", handle)

def start_web():
    runner = web.AppRunner(app)
    loop = asyncio.get_event_loop()
    
    async def start():
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
    
    loop.create_task(start())

start_web()

# ===== Run the Bot =====

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("❌ Token is missing. Set the DISCORD_BOT_TOKEN environment variable.")
else:
    bot.run(TOKEN)
