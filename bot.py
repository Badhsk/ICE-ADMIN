import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import os
import time

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

cooldowns = {}
warnings = {}

def anti_spam(user_id):
    now = time.time()
    if user_id in cooldowns:
        if now - cooldowns[user_id] < 2:
            return True
    cooldowns[user_id] = now
    return False

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot Ready")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if anti_spam(message.author.id):
        await message.delete()
    await bot.process_commands(message)

@bot.tree.command(name="طرد")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str="بدون سبب"):
    await user.kick(reason=reason)
    await interaction.response.send_message("تم الطرد")

@bot.tree.command(name="حظر")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str="بدون سبب"):
    await user.ban(reason=reason)
    await interaction.response.send_message("تم الحظر")

@bot.tree.command(name="اسكات")
async def mute(interaction: discord.Interaction, user: discord.Member, minutes: int):
    await user.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message("تم الاسكات")

@bot.tree.command(name="فك_اسكات")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    await user.timeout(None)
    await interaction.response.send_message("تم فك الاسكات")

@bot.tree.command(name="مسح")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("تم المسح", ephemeral=True)

@bot.tree.command(name="تحذير")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    warnings.setdefault(user.id, []).append(reason)
    await interaction.response.send_message("تم التحذير")

@bot.tree.command(name="تحذيرات")
async def warns(interaction: discord.Interaction, user: discord.Member):
    w = warnings.get(user.id, [])
    await interaction.response.send_message(str(w))

@bot.tree.command(name="الأوامر")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "/طرد /حظر /اسكات /فك_اسكات /مسح /تحذير /تحذيرات"
    )

bot.run(os.getenv("TOKEN"))
