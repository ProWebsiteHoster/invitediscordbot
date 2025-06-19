import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to track resets and all-time invites
invite_data = {}

@bot.event
async def on_ready():
    print(f'✅ Bot is ready. Logged in as {bot.user}')

# Get total invites by a member
async def get_invite_count(member):
    invites = await member.guild.invites()
    total = 0
    for invite in invites:
        if invite.inviter == member:
            total += invite.uses
    return total

# Command 1: !checkinvites
@bot.command(name="checkinvites")
async def check_invites(ctx, member: discord.Member = None):
    member = member or ctx.author
    total = await get_invite_count(member)

    valid = total
    if member.id in invite_data:
        valid = total - invite_data[member.id]['reset_total']
    
    await ctx.send(
        f"{member.mention}\n"
        f"✅ Valid Invites: **{valid}**\n"
        f"📊 All Time Invites: **{total}**"
    )

# Command 2: !checkinviteeligibility
@bot.command(name="checkinviteeligibility")
async def check_invite_eligibility(ctx, member: discord.Member = None):
    member = member or ctx.author
    total = await get_invite_count(member)

    valid = total
    if member.id in invite_data:
        valid = total - invite_data[member.id]['reset_total']

    if valid >= 3:
        await ctx.send(
            f"{member.mention} ✅ You are eligible for claiming invite rewards since you have **{valid}** invites."
        )
        mod_role = discord.utils.get(ctx.guild.roles, name="Moderator")
        if mod_role:
            await ctx.send(f"{mod_role.mention} 🔔 {member.mention} is eligible to claim.")
    else:
        await ctx.send(
            f"{member.mention} ❌ You do not have the required number of invites to claim right now.\n"
            f"Kindly invite more people to the server and try again!"
        )

# Command 3: !inviteclaimcount
@bot.command(name="inviteclaimcount")
async def invite_claim_count(ctx, member: discord.Member = None):
    member = member or ctx.author
    total = await get_invite_count(member)

    valid = total
    if member.id in invite_data:
        valid = total - invite_data[member.id]['reset_total']

    claims = valid // 3
    await ctx.send(
        f"{member.mention} 🎁 You can claim **{claims}** time(s) based on **{valid}** valid invites."
    )

# Command 4: !resetinvites (only for authorized roles)
@bot.command(name="resetinvites")
@commands.has_any_role("Founder", "Owner", "Moderation Team", "Moderator")
async def reset_invites(ctx, member: discord.Member):
    total = await get_invite_count(member)
    invite_data[member.id] = {'reset_total': total}
    await ctx.send(
        f"🔄 {member.mention}'s invites have been reset.\n"
        f"📊 Old invites are now counted in 'All Time Invites'."
    )

# Start the keep-alive server
keep_alive()

# Replace with your actual token
import os
bot.run(os.getenv("TOKEN"))

import time
while True:
    time.sleep(60)

