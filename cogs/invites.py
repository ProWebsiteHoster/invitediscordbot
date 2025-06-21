import discord
from discord.ext import commands
from discord import app_commands

invite_data = {}

class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_invite_count(self, member):
        invites = await member.guild.invites()
        total = sum(invite.uses for invite in invites if invite.inviter == member)
        return total

    @app_commands.command(name="checkinvites", description="Check your or someone else's invite count.")
    async def checkinvites(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        total = await self.get_invite_count(user)
        valid = total - invite_data.get(user.id, {}).get('reset_total', 0)

        await interaction.response.send_message(
            f"{user.mention}\n✅ Valid Invites: **{valid}**\n📊 All Time Invites: **{total}**"
        )

    @app_commands.command(name="checkinviteeligibility", description="Check if someone is eligible for rewards.")
    async def checkinviteeligibility(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        total = await self.get_invite_count(user)
        valid = total - invite_data.get(user.id, {}).get('reset_total', 0)

        if valid >= 3:
            mod_role = discord.utils.get(interaction.guild.roles, name="Moderator")
            await interaction.response.send_message(
                f"{user.mention} ✅ You are eligible to claim rewards! ({valid} invites)\n"
                f"{mod_role.mention if mod_role else ''} 🔔 {user.mention} is eligible to claim."
            )
        else:
            await interaction.response.send_message(
                f"{user.mention} ❌ Not enough invites. Please invite more people."
            )

    @app_commands.command(name="inviteclaimcount", description="Check how many times you can claim.")
    async def inviteclaimcount(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        total = await self.get_invite_count(user)
        valid = total - invite_data.get(user.id, {}).get('reset_total', 0)
        claims = valid // 3

        await interaction.response.send_message(
            f"{user.mention} 🎁 You can claim **{claims}** time(s) based on **{valid}** invites."
        )

    @app_commands.command(name="resetinvites", description="Reset a user's invites (mod only).")
    async def resetinvites(self, interaction: discord.Interaction, user: discord.Member):
        roles = [r.name for r in interaction.user.roles]
        if any(r in ["Founder", "Owner", "Moderation Team", "Moderator"] for r in roles):
            total = await self.get_invite_count(user)
            invite_data[user.id] = {"reset_total": total}
            await interaction.response.send_message(
                f"🔄 {user.mention}'s invites have been reset. Old invites still count as all-time."
            )
        else:
            await interaction.response.send_message("❌ You are not allowed to use this command.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Invites(bot))
