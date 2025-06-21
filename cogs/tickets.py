import discord
from discord.ext import commands
from discord import app_commands

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="createticket", description="Create a support ticket.")
    async def createticket(self, interaction: discord.Interaction):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        category = discord.utils.get(interaction.guild.categories, name="Tickets")
        if not category:
            category = await interaction.guild.create_category("Tickets")

        channel = await category.create_text_channel(
            f"ticket-{interaction.user.name}", overwrites=overwrites
        )
        await interaction.response.send_message(
            f"🎫 Ticket created: {channel.mention}", ephemeral=True
        )
        await channel.send(f"{interaction.user.mention} Thank you! A team member will help you soon.")

    @app_commands.command(name="closeticket", description="Close the ticket you're in.")
    async def closeticket(self, interaction: discord.Interaction):
        if "ticket" in interaction.channel.name:
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("❌ This is not a ticket channel.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
