import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from datetime import timedelta
import os
import time
import random

# ================= WEB SERVER =================
app = Flask("")

@app.route("/")
def home():
    return "Bot is running"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    Thread(target=run).start()

# ================= BOT =================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= DATA =================

credits = {}
afk = {}
warnings = {}

# ================= READY =================

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands")
    print(f"Logged in as {bot.user}")

# ================= BASIC =================

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

# ================= ROLES =================

@bot.tree.command(name="اعطاء_رتبة")
async def addrole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await interaction.response.send_message("✅ تم إعطاء رتبة")

@bot.tree.command(name="مسح_رتب")
async def removeroles(interaction: discord.Interaction, user: discord.Member):
    await user.edit(roles=[])
    await interaction.response.send_message("🧹 تم مسح الرتب")

@bot.tree.command(name="تغيير_ايقونة_رتبة")
async def roleicon(interaction: discord.Interaction, role: discord.Role, url: str):
    await role.edit(display_icon=url)
    await interaction.response.send_message("🎭 تم تغيير أيقونة الرتبة")

# ================= CHAT CONTROL =================

@bot.tree.command(name="اقفال_شات")
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 تم القفل")

@bot.tree.command(name="فتح_شات")
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 تم الفتح")

@bot.tree.command(name="اخفاء")
async def hide(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.set_permissions(interaction.guild.default_role, view_channel=False)
    await interaction.response.send_message("🙈 تم الإخفاء")

@bot.tree.command(name="اظهار")
async def show(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.set_permissions(interaction.guild.default_role, view_channel=True)
    await interaction.response.send_message("👀 تم الإظهار")

# ================= TICKET =================

@bot.tree.command(name="تيكت")
async def ticket(interaction: discord.Interaction):

    guild = interaction.guild

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True)
    }

    ch = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
    await ch.send("🎟️ تيكت مفتوح")
    await interaction.response.send_message("تم فتح تيكت", ephemeral=True)

@bot.tree.command(name="اغلاق_تيكت")
async def close(interaction: discord.Interaction):
    await interaction.channel.delete()

# ================= PROFILE =================

@bot.tree.command(name="بروفايل")
async def profile(interaction: discord.Interaction, user: discord.Member=None):
    user = user or interaction.user
    await interaction.response.send_message(user.avatar.url)

@bot.tree.command(name="صورة_عشوائية")
async def randompfp(interaction: discord.Interaction):
    url = f"https://i.pravatar.cc/300?img={random.randint(1,70)}"
    await interaction.response.send_message(url)

# ================= CREDITS =================

@bot.tree.command(name="كريديت")
async def credit(interaction: discord.Interaction, user: discord.Member=None):
    user = user or interaction.user
    await interaction.response.send_message(f"💰 {credits.get(user.id,0)}")

@bot.tree.command(name="تحويل")
async def transfer(interaction: discord.Interaction, user: discord.Member, amount: int):

    if credits.get(interaction.user.id,0) < amount:
        return await interaction.response.send_message("❌ ما عندك كريديت")

    credits[interaction.user.id] -= amount
    credits[user.id] = credits.get(user.id,0) + amount

    await interaction.response.send_message("💸 تم التحويل")

# ================= AFK =================

@bot.tree.command(name="afk")
async def setafk(interaction: discord.Interaction, reason: str="AFK"):
    afk[interaction.user.id] = reason
    await interaction.response.send_message("😴 تم AFK")

# ================= WARN =================

@bot.tree.command(name="تحذير")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    warnings.setdefault(user.id, []).append(reason)
    await interaction.response.send_message("⚠️ تم التحذير")

@bot.tree.command(name="تحذيرات")
async def showwarns(interaction: discord.Interaction, user: discord.Member):
    w = warnings.get(user.id, [])
    await interaction.response.send_message(f"📋 {len(w)} تحذيرات")

# ================= USER INFO =================

@bot.tree.command(name="معلومات_عضو")
async def userinfo(interaction: discord.Interaction, user: discord.Member=None):

    user = user or interaction.user

    age = (discord.utils.utcnow() - user.created_at).days

    await interaction.response.send_message(
        f"""
👤 {user.name}
📅 انشأ الحساب منذ: {age} يوم
🆔 {user.id}
"""
    )

@bot.tree.command(name="فحص_عضو")
async def check(interaction: discord.Interaction, user: discord.Member):

    age = (discord.utils.utcnow() - user.created_at).days

    status = "🚨 مشبوه" if age < 7 else "⚠️ جديد" if age < 30 else "✅ طبيعي"

    await interaction.response.send_message(f"{user.mention} → {status}")

# ================= HELP =================

@bot.tree.command(name="الأوامر")
async def help(interaction: discord.Interaction):

    await interaction.response.send_message("""
🤖 كل الأوامر:

🛡️ إدارة:
/طرد /حظر /اسكات /فك_اسكات /مسح

🎭 رتب:
/اعطاء_رتبة /مسح_رتب /تغيير_ايقونة_رتبة

🔒 شات:
/اقفال_شات /فتح_شات /اخفاء /اظهار

🎟️ تيكت:
/تيكت /اغلاق_تيكت

💰 اقتصاد:
/كريديت /تحويل

👤:
/معلومات_عضو /فحص_عضو /بروفايل

😴:
/afk

📜:
/الأوامر
""")

# ================= RUN =================

keep_alive()
bot.run(os.getenv("TOKEN"))
