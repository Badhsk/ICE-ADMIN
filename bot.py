import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import time

# ================= WEB SERVER =================
app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= DISCORD BOT =================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

cooldowns = {}

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
    print(f"Bot Ready: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if anti_spam(message.author.id):
        await message.delete()

    await bot.process_commands(message)

# ================= COMMANDS =================

@bot.tree.command(name="طرد")
async def kick(interaction: discord.Interaction, user: discord.Member):
    await user.kick()
    await interaction.response.send_message("👢 تم الطرد")

@bot.tree.command(name="حظر")
async def ban(interaction: discord.Interaction, user: discord.Member):
    await user.ban()
    await interaction.response.send_message("⛔ تم الحظر")

@bot.tree.command(name="اسكات")
async def mute(interaction: discord.Interaction, user: discord.Member, minutes: int):
    from datetime import timedelta
    await user.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message("🔇 تم الاسكات")

@bot.tree.command(name="فك_اسكات")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    await user.timeout(None)
    await interaction.response.send_message("🔊 تم فك الاسكات")

@bot.tree.command(name="مسح")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("🧹 تم المسح", ephemeral=True)

@bot.tree.command(name="الأوامر")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "/طرد /حظر /اسكات /فك_اسكات /مسح"
    )

# ================= RUN =================
keep_alive()
bot.run(os.getenv("TOKEN"))
