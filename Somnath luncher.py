import customtkinter as ctk
import tkinter as tk
import minecraft_launcher_lib
import subprocess
import threading
import random
import os

ctk.set_appearance_mode("light")

app = ctk.CTk()
app.geometry("620x520")
app.title("Somnath Launcher")
app.resizable(False, False)

minecraft_dir = minecraft_launcher_lib.utils.get_minecraft_directory()

# --- ANIMATED MINECRAFT CANVAS BACKGROUND ---
bg_canvas = tk.Canvas(app, width=620, height=520, highlightthickness=0, bd=0)
bg_canvas.place(x=0, y=0)

# Draw Vibrant Sky & Sun
bg_canvas.configure(bg="#78A7FF")  # Bright Minecraft Sky Blue
bg_canvas.create_rectangle(0, 0, 620, 180, fill="#639BFF", outline="")
bg_canvas.create_rectangle(0, 180, 620, 340, fill="#8BB8FF", outline="")

# Glowing Pixel Sun
sun_halo = bg_canvas.create_rectangle(490, 35, 565, 110, fill="#FFF3B0", outline="")
sun_core = bg_canvas.create_rectangle(502, 47, 553, 98, fill="#FFD60A", outline="#F59E0B", width=3)

# Draw Layered Minecraft Grass & Dirt Terrain at Bottom
bg_canvas.create_rectangle(0, 415, 620, 435, fill="#55A630", outline="")  # Bright Grass Top
bg_canvas.create_rectangle(0, 435, 620, 445, fill="#386641", outline="")  # Grass Shadow Edge
bg_canvas.create_rectangle(0, 445, 620, 520, fill="#7F4F24", outline="")  # Dirt Base

# Pixel Dirt Texture Speckles
for _ in range(45):
    dx = random.randint(0, 610)
    dy = random.randint(450, 510)
    color = random.choice(["#582F0E", "#936639", "#653A18"])
    bg_canvas.create_rectangle(dx, dy, dx+8, dy+8, fill=color, outline="")

# Animated Clouds Data
clouds = [
    {"x": 40, "y": 55, "w": 110, "h": 26, "speed": 0.6},
    {"x": 260, "y": 95, "w": 140, "h": 30, "speed": 0.4},
    {"x": 460, "y": 145, "w": 95, "h": 22, "speed": 0.75},
]
cloud_items = []
for c in clouds:
    shadow = bg_canvas.create_rectangle(c["x"], c["y"]+6, c["x"]+c["w"], c["y"]+c["h"]+6, fill="#DCE8FF", outline="")
    body = bg_canvas.create_rectangle(c["x"], c["y"], c["x"]+c["w"], c["y"]+c["h"], fill="#FFFFFF", outline="")
    cloud_items.append((shadow, body, c))

# Animated Floating XP / Emerald Sparkle Particles
particles = []
for _ in range(18):
    px = random.randint(20, 600)
    py = random.randint(150, 410)
    size = random.choice([4, 6])
    p_color = random.choice(["#AACC00", "#FFD60A", "#FFFFFF", "#80ED99"])
    item = bg_canvas.create_rectangle(px, py, px+size, py+size, fill=p_color, outline="")
    particles.append([item, px, py, random.uniform(0.5, 1.3), size])

# Pulse state for Play Button & Sun
pulse_step = 0

def animate_scene():
    global pulse_step
    pulse_step += 1

    # Move Clouds across the sky
    for shadow, body, c in cloud_items:
        c["x"] += c["speed"]
        if c["x"] > 640:
            c["x"] = -c["w"] - 20
        bg_canvas.coords(shadow, c["x"], c["y"]+6, c["x"]+c["w"], c["y"]+c["h"]+6)
        bg_canvas.coords(body, c["x"], c["y"], c["x"]+c["w"], c["y"]+c["h"])

    # Float Sparkle Particles Upward
    for p in particles:
        item, px, py, speed, size = p
        py -= speed
        if py < 120:
            py = 410
            px = random.randint(20, 600)
        p[1], p[2] = px, py
        bg_canvas.coords(item, px, py, px+size, py+size)

    # Subtle Sun Glow Pulse
    if (pulse_step // 15) % 2 == 0:
        bg_canvas.coords(sun_halo, 488, 33, 567, 112)
    else:
        bg_canvas.coords(sun_halo, 493, 38, 562, 107)

    app.after(30, animate_scene)

# --- LAUNCHER LOGIC ---
def fetch_versions():
    try:
        all_versions = minecraft_launcher_lib.utils.get_version_list()
        filtered_versions = []
        for v in all_versions:
            vid = v["id"]
            if v["type"] not in ["release", "snapshot"]:
                continue
            filtered_versions.append(vid)
            if vid == "1.12":
                break
        if filtered_versions:
            version_dropdown.configure(values=filtered_versions)
            version_dropdown.set(filtered_versions)
            status_label.configure(text=f"Ready • {len(filtered_versions)} versions (1.12 to Latest)", text_color="#2B7A0B")
    except Exception:
        status_label.configure(text="Offline mode: Could not fetch latest versions", text_color="#D97706")

def find_installed_version(keyword, mc_version, exclude=None):
    versions_folder = os.path.join(minecraft_dir, "versions")
    if not os.path.exists(versions_folder):
        return None
    for folder in os.listdir(versions_folder):
        if keyword.lower() in folder.lower() and mc_version in folder:
            if exclude and exclude.lower() in folder.lower():
                continue
            return folder
    return None

def launch_game():
    username = username_entry.get().strip() or "Player"
    version = version_dropdown.get()
    loader = loader_dropdown.get()
    
    if version == "Loading versions...":
        return

    status_label.configure(text=f"Preparing {loader} {version}...", text_color="#D97706")
    play_button.configure(state="disabled")

    def run():
        try:
            launch_version_id = version
            if loader == "Vanilla":
                minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_dir)
            elif loader == "Fabric":
                status_label.configure(text=f"Installing Fabric {version}...", text_color="#D97706")
                minecraft_launcher_lib.mod_loader.get_mod_loader("fabric").install(version, minecraft_dir)
                launch_version_id = find_installed_version("fabric-loader", version) or version
            elif loader == "Forge":
                status_label.configure(text=f"Installing Forge {version}...", text_color="#D97706")
                minecraft_launcher_lib.mod_loader.get_mod_loader("forge").install(version, minecraft_dir)
                launch_version_id = find_installed_version("forge", version, exclude="neoforge") or version
            elif loader == "NeoForge":
                status_label.configure(text=f"Installing NeoForge {version}...", text_color="#D97706")
                minecraft_launcher_lib.mod_loader.get_mod_loader("neoforge").install(version, minecraft_dir)
                launch_version_id = find_installed_version("neoforge", version) or version

            options = {
                "username": username,
                "uuid": "",
                "token": "",
                "jvmArguments": ["-Xmx3G", "-Xms1G"]
            }
            command = minecraft_launcher_lib.command.get_minecraft_command(launch_version_id, minecraft_dir, options)
            status_label.configure(text=f"Launching {launch_version_id} (3GB RAM)...", text_color="#2B7A0B")
            subprocess.run(command)
        except Exception as e:
            status_label.configure(text=f"Error: {str(e)}", text_color="#DC2626")
        finally:
            play_button.configure(state="normal")
            status_label.configure(text="Ready to play", text_color="#4B5563")

    threading.Thread(target=run, daemon=True).start()

# --- FOREGROUND WHITE & COLORFUL UI CARD ---
card = ctk.CTkFrame(
    app, 
    width=410, 
    height=405, 
    fg_color="#FFFFFF", 
    border_width=3, 
    border_color="#2B7A0B", 
    corner_radius=8
)
card.place(relx=0.5, rely=0.47, anchor="center")
card.pack_propagate(False)

# Colorful Grass-Green Title Header inside Card
title_banner = ctk.CTkFrame(card, fg_color="#3C8527", corner_radius=4, height=52)
title_banner.pack(fill="x", padx=12, pady=(12, 10))
title_banner.pack_propagate(False)

title_label = ctk.CTkLabel(
    title_banner, 
    text="⚔ SOMNATH LAUNCHER ⚔", 
    font=("Consolas", 20, "bold"), 
    text_color="#FFFFFF"
)
title_label.pack(expand=True)

# Username Entry
ctk.CTkLabel(card, text="PLAYER USERNAME", font=("Consolas", 11, "bold"), text_color="#374151").pack(pady=(4, 2))
username_entry = ctk.CTkEntry(
    card, 
    placeholder_text="Enter Username...", 
    width=320, 
    height=35,
    corner_radius=4,
    border_width=2,
    border_color="#3B82F6",
    fg_color="#F9FAFB",
    text_color="#111827",
    font=("Consolas", 13, "bold")
)
username_entry.pack(pady=(0, 8))

# Version Dropdown
ctk.CTkLabel(card, text="GAME VERSION (1.12 - LATEST)", font=("Consolas", 11, "bold"), text_color="#374151").pack(pady=(2, 2))
version_dropdown = ctk.CTkOptionMenu(
    card, 
    values=["Loading versions..."], 
    width=320, 
    height=35,
    corner_radius=4,
    fg_color="#2563EB",
    button_color="#1D4ED8",
    button_hover_color="#1E40AF",
    text_color="#FFFFFF",
    font=("Consolas", 13, "bold")
)
version_dropdown.pack(pady=(0, 8))

# Loader Dropdown
ctk.CTkLabel(card, text="MOD LOADER", font=("Consolas", 11, "bold"), text_color="#374151").pack(pady=(2, 2))
loader_dropdown = ctk.CTkOptionMenu(
    card, 
    values=["Vanilla", "Fabric", "Forge", "NeoForge"], 
    width=320, 
    height=35,
    corner_radius=4,
    fg_color="#7C3AED",
    button_color="#6D28D9",
    button_hover_color="#5B21B6",
    text_color="#FFFFFF",
    font=("Consolas", 13, "bold")
)
loader_dropdown.pack(pady=(0, 12))

# Vibrant Minecraft Emerald-Green Play Button
play_button = ctk.CTkButton(
    card, 
    text="▶ PLAY (3GB RAM)", 
    font=("Consolas", 16, "bold"), 
    width=320, 
    height=46,
    corner_radius=4,
    border_width=2,
    border_color="#1E5611",
    fg_color="#3C8527",
    hover_color="#2E6B1D",
    text_color="#FFFFFF",
    command=launch_game
)
play_button.pack(pady=(4, 8))

# Status Footer
status_label = ctk.CTkLabel(card, text="Fetching versions from Mojang...", font=("Consolas", 11, "bold"), text_color="#2B7A0B")
status_label.pack(pady=(2, 6))

# Start Animations & Fetch Versions
animate_scene()
threading.Thread(target=fetch_versions, daemon=True).start()

app.mainloop()
