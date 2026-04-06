import serial
import pygame
import random
import math
import time
import os

PORT = "/dev/cu.usbserial-59270096981"
BAUD = 115200

WIDTH = 1280
HEIGHT = 760
GROUND_Y = HEIGHT // 2 + 20
GARDEN_WIDTH = 960
PANEL_X = GARDEN_WIDTH

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bloomscape")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont("georgia", 54, bold=True)
subtitle_font = pygame.font.SysFont("georgia", 22, italic=True)
info_font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 19)

PANEL_BG = (247, 241, 233)
PANEL_LINE = (218, 199, 180)
TEXT_MAIN = (88, 62, 54)
TEXT_SUB = (134, 103, 94)
GREEN_ACCENT = (86, 142, 84)
BLUE_ACCENT = (72, 129, 197)
PINK_ACCENT = (181, 94, 109)

ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)

def load_sound(filename):
    if os.path.exists(filename):
        try:
            return pygame.mixer.Sound(filename)
        except pygame.error:
            print(f"Could not load sound: {filename}")
            return None
    print(f"Missing sound file: {filename}")
    return None

plant_sound = load_sound("plant.wav")
water_sound = load_sound("water.mp3")
cut_sound = load_sound("cut.mp3")

if os.path.exists("joyful.mp3"):
    try:
        pygame.mixer.music.load("joyful.mp3")
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Could not load joyful.mp3")

current_mode = "PLANT"
flowers = []
bouquet = []
petals = []
drops = []
clouds = []
sparkles = []

for _ in range(5):
    clouds.append({
        "x": random.randint(0, GARDEN_WIDTH - 140),
        "y": random.randint(45, 180),
        "speed": random.uniform(0.12, 0.35),
        "size": random.randint(75, 120)
    })

grass_texture = []
for _ in range(550):
    grass_texture.append((
        random.randint(0, GARDEN_WIDTH - 1),
        random.randint(GROUND_Y, HEIGHT - 1),
        random.choice([
            (78, 145, 72),
            (86, 155, 76),
            (92, 162, 82),
            (68, 132, 64)
        ])
    ))

mid_blades = []
for i in range(0, GARDEN_WIDTH, 10):
    mid_blades.append((
        i,
        random.randint(10, 22),
        random.randint(-4, 4),
        random.choice([
            (70, 145, 68),
            (76, 152, 72),
            (82, 160, 76)
        ])
    ))

front_blades = []
for i in range(0, GARDEN_WIDTH, 14):
    front_blades.append((
        i,
        random.randint(18, 34),
        random.randint(-6, 6),
        random.choice([
            (58, 126, 58),
            (64, 134, 62),
            (72, 142, 68)
        ])
    ))

class Flower:
    def __init__(self, flower_type, x, y):
        self.type = flower_type
        self.x = x
        self.y = y
        self.stage = 0
        self.swing_offset = random.uniform(0, math.pi * 2)
        self.size_variation = random.uniform(0.92, 1.10)
        self.curve = random.uniform(-8, 8)

    def water(self):
        if self.stage < 3:
            self.stage += 1

    def get_scale(self):
        return [0.34, 0.56, 0.80, 1.02][self.stage] * self.size_variation

    def draw(self, surface, t):
        sway = math.sin(t * 0.002 + self.swing_offset) * 3
        x = self.x + sway
        scale = self.get_scale()

        if self.stage == 0:
            draw_sprout(surface, x, self.y, self.type, scale)
            return

        draw_shadow(surface, x, self.y, scale)

        if self.type == "frangipani":
            draw_frangipani(surface, x, self.y, scale, self.curve)
        elif self.type == "daisy":
            draw_daisy(surface, x, self.y, scale, self.curve)
        elif self.type == "rose":
            draw_rose(surface, x, self.y, scale, self.curve)
        elif self.type == "tulip":
            draw_tulip(surface, x, self.y, scale, self.curve)
        elif self.type == "forget_me_not":
            draw_forget_me_not(surface, x, self.y, scale, self.curve)

class Petal:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(-2.1, -0.6)
        self.gravity = 0.05
        self.life = random.randint(35, 60)
        self.color = color
        self.size = random.randint(3, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, min(255, int(255 * (self.life / 60))))
        s = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*self.color, alpha), (0, 0, self.size * 4, self.size * 2.5))
        surface.blit(s, (self.x, self.y))

class WaterDrop:
    def __init__(self, x, y):
        self.x = x
        self.y = y - 90
        self.target_y = y - 10
        self.speed = 5.5
        self.done = False

    def update(self):
        self.y += self.speed
        if self.y >= self.target_y:
            self.done = True
            for _ in range(5):
                sparkles.append(Sparkle(
                    self.x + random.randint(-8, 8),
                    self.y + random.randint(-5, 5),
                    (120, 200, 255)
                ))

    def draw(self, surface):
        pygame.draw.ellipse(surface, (100, 180, 255), (self.x - 5, self.y - 9, 10, 18))
        pygame.draw.ellipse(surface, (180, 225, 255), (self.x - 2, self.y - 6, 4, 8))

class Sparkle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = random.randint(12, 22)
        self.radius = random.randint(2, 4)

    def update(self):
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / 22))
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (10, 10), self.radius)
        surface.blit(s, (self.x - 10, self.y - 10))

def play_sound(sound):
    if sound:
        sound.play()

def spawn_petals(x, y, flower_type):
    colors = {
        "rose": (210, 40, 70),
        "daisy": (255, 255, 255),
        "frangipani": (255, 240, 180),
        "tulip": (220, 90, 135),
        "forget_me_not": (110, 150, 255),
    }
    color = colors.get(flower_type, (255, 255, 255))
    for _ in range(10):
        petals.append(Petal(x, y, color))

def find_open_spot():
    for _ in range(150):
        x = random.randint(85, GARDEN_WIDTH - 90)
        y = random.randint(GROUND_Y + 65, HEIGHT - 70)

        too_close = False
        for flower in flowers:
            if abs(flower.x - x) < 48 and abs(flower.y - y) < 36:
                too_close = True
                break

        if not too_close:
            return x, y
    return None

def plant_flower(flower_type):
    spot = find_open_spot()
    if spot is not None:
        x, y = spot
        flowers.append(Flower(flower_type, x, y))
        play_sound(plant_sound)

def water_flower(flower_type):
    candidates = [f for f in flowers if f.type == flower_type and f.stage < 3]
    if candidates:
        flower = min(candidates, key=lambda f: f.stage)
        flower.water()
        drops.append(WaterDrop(flower.x, flower.y))
        spawn_petals(flower.x, flower.y - 24, flower.type)
        play_sound(water_sound)

def cut_flower(flower_type):
    candidates = [f for f in flowers if f.type == flower_type and f.stage > 0]
    if candidates:
        flower = candidates[0]
        bouquet.append(flower.type)
        spawn_petals(flower.x, flower.y - 20, flower.type)
        flowers.remove(flower)
        play_sound(cut_sound)

def handle_flower_touch(flower_type):
    if current_mode == "PLANT":
        plant_flower(flower_type)
    elif current_mode == "WATER":
        water_flower(flower_type)
    elif current_mode == "CUT":
        cut_flower(flower_type)

def draw_gradient_sky(surface):
    top = (126, 188, 255)
    mid = (236, 214, 255)
    for y in range(GROUND_Y):
        ratio = y / GROUND_Y
        r = int(top[0] * (1 - ratio) + mid[0] * ratio)
        g = int(top[1] * (1 - ratio) + mid[1] * ratio)
        b = int(top[2] * (1 - ratio) + mid[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (GARDEN_WIDTH, y))

def draw_sun(surface):
    sun_x = 760
    sun_y = 105

    for radius, alpha in [(95, 20), (75, 28), (58, 40)]:
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 228, 150, alpha), (radius, radius), radius)
        surface.blit(glow, (sun_x - radius, sun_y - radius))

    for angle in range(0, 360, 20):
        ray_len = 95
        inner = 48
        x1 = sun_x + math.cos(math.radians(angle)) * inner
        y1 = sun_y + math.sin(math.radians(angle)) * inner
        x2 = sun_x + math.cos(math.radians(angle)) * ray_len
        y2 = sun_y + math.sin(math.radians(angle)) * ray_len
        pygame.draw.line(surface, (255, 220, 140), (x1, y1), (x2, y2), 2)

    pygame.draw.circle(surface, (255, 236, 170), (sun_x, sun_y), 42)
    pygame.draw.circle(surface, (255, 244, 200), (sun_x - 8, sun_y - 8), 24)

    haze = pygame.Surface((GARDEN_WIDTH, 180), pygame.SRCALPHA)
    for y in range(180):
        alpha = max(0, 55 - y // 4)
        pygame.draw.line(haze, (255, 220, 170, alpha), (0, y), (GARDEN_WIDTH, y))
    surface.blit(haze, (0, GROUND_Y - 180))

def draw_cloud(surface, x, y, size):
    width = int(size * 1.8)
    height = int(size * 0.9)
    cloud = pygame.Surface((width, height), pygame.SRCALPHA)

    shadow = (190, 205, 225, 35)
    white = (255, 255, 255, 225)

    pygame.draw.ellipse(cloud, shadow, (int(width * 0.10), int(height * 0.42), int(width * 0.70), int(height * 0.28)))

    pygame.draw.ellipse(cloud, white, (int(width * 0.08), int(height * 0.36), int(width * 0.68), int(height * 0.30)))
    pygame.draw.circle(cloud, white, (int(width * 0.24), int(height * 0.46)), int(size * 0.22))
    pygame.draw.circle(cloud, white, (int(width * 0.42), int(height * 0.30)), int(size * 0.28))
    pygame.draw.circle(cloud, white, (int(width * 0.62), int(height * 0.42)), int(size * 0.22))
    pygame.draw.circle(cloud, white, (int(width * 0.52), int(height * 0.50)), int(size * 0.18))

    surface.blit(cloud, (x, y))

def draw_ground(surface):
    pygame.draw.rect(surface, (96, 168, 88), (0, GROUND_Y, GARDEN_WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(surface, (84, 154, 78), (0, GROUND_Y + 35, GARDEN_WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(surface, (72, 138, 68), (0, GROUND_Y + 110, GARDEN_WIDTH, HEIGHT - GROUND_Y))

    highlight = pygame.Surface((GARDEN_WIDTH, 90), pygame.SRCALPHA)
    for y in range(90):
        alpha = max(0, 35 - y // 3)
        pygame.draw.line(highlight, (170, 220, 130, alpha), (0, y), (GARDEN_WIDTH, y))
    surface.blit(highlight, (0, GROUND_Y))

    for x, y, color in grass_texture:
        surface.set_at((x, y), color)

    for i, blade_height, tilt, color in mid_blades:
        pygame.draw.line(surface, color, (i, GROUND_Y + 6), (i + tilt, GROUND_Y - blade_height), 2)

    for i, blade_height, tilt, color in front_blades:
        pygame.draw.line(surface, color, (i, HEIGHT - 6), (i + tilt, HEIGHT - blade_height), 2)

def mode_color(mode):
    if mode == "PLANT":
        return GREEN_ACCENT
    if mode == "WATER":
        return BLUE_ACCENT
    return PINK_ACCENT

def draw_panel(surface):
    pygame.draw.rect(surface, PANEL_BG, (PANEL_X, 0, WIDTH - PANEL_X, HEIGHT))
    pygame.draw.line(surface, PANEL_LINE, (PANEL_X, 0), (PANEL_X, HEIGHT), 2)

    mode_label = small_font.render("Mode", True, TEXT_SUB)
    mode_text = info_font.render(current_mode.lower(), True, mode_color(current_mode))
    help1 = small_font.render("1 tap plant", True, TEXT_SUB)
    help2 = small_font.render("2 taps water", True, TEXT_SUB)
    help3 = small_font.render("3 taps cut", True, TEXT_SUB)
    help4 = small_font.render("Tap reset to clear garden", True, TEXT_SUB)
    bouquet_label = info_font.render("Bouquet", True, TEXT_MAIN)

    surface.blit(mode_label, (PANEL_X + 28, 54))
    surface.blit(mode_text, (PANEL_X + 28, 82))

    pygame.draw.line(surface, PANEL_LINE, (PANEL_X + 28, 140), (WIDTH - 24, 140), 1)

    surface.blit(help1, (PANEL_X + 28, 168))
    surface.blit(help2, (PANEL_X + 28, 198))
    surface.blit(help3, (PANEL_X + 28, 228))
    surface.blit(help4, (PANEL_X + 28, 258))

    pygame.draw.line(surface, PANEL_LINE, (PANEL_X + 28, 320), (WIDTH - 24, 320), 1)
    surface.blit(bouquet_label, (PANEL_X + 28, 344))

def draw_background(surface):
    draw_gradient_sky(surface)
    draw_sun(surface)
    for cloud in clouds:
        draw_cloud(surface, cloud["x"], cloud["y"], cloud["size"])
    draw_ground(surface)
    draw_panel(surface)

def draw_shadow(surface, x, y, scale):
    shadow_w = int(34 * scale)
    shadow_h = int(12 * scale)
    s = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 38), (0, 0, shadow_w * 2, shadow_h * 2))
    surface.blit(s, (x - shadow_w, y + 35 * scale))

def draw_curved_stem(surface, x, y, scale, curve):
    base_y = y + int(48 * scale)
    mid_x = x + curve * 0.4
    top = (int(x), int(y))
    mid = (int(mid_x), int(y + 18 * scale))
    bottom = (int(x), int(base_y))
    pygame.draw.lines(surface, (56, 142, 73), False, [bottom, mid, top], max(2, int(4 * scale)))

def draw_sprout(surface, x, y, flower_type, scale):
    stem_h = int(24 * scale) + 8
    pygame.draw.line(surface, (64, 150, 79), (int(x), int(y + 10)), (int(x), int(y + 10 + stem_h)), 3)
    pygame.draw.ellipse(surface, (88, 178, 96), (x - 12, y + 12, 14, 8))
    pygame.draw.ellipse(surface, (88, 178, 96), (x - 1, y + 18, 14, 8))

    bud_colors = {
        "rose": (191, 38, 67),
        "daisy": (236, 210, 82),
        "frangipani": (255, 235, 190),
        "tulip": (224, 98, 140),
        "forget_me_not": (120, 160, 255),
    }
    pygame.draw.circle(surface, bud_colors.get(flower_type, (255, 255, 255)), (int(x), int(y + 10)), 6)

def draw_frangipani(surface, x, y, scale, curve=0):
    draw_curved_stem(surface, x, y, scale, curve)
    pygame.draw.ellipse(surface, (80, 165, 88), (x - 14 * scale, y + 18 * scale, 16 * scale, 9 * scale))
    pygame.draw.ellipse(surface, (80, 165, 88), (x + 1 * scale, y + 24 * scale, 16 * scale, 9 * scale))

    petal_outer = (255, 247, 224)
    petal_inner = (255, 220, 90)
    ring = 14 * scale
    radius = max(6, int(13 * scale))

    for angle in range(0, 360, 72):
        px = x + math.cos(math.radians(angle)) * ring
        py = y + math.sin(math.radians(angle)) * ring
        pygame.draw.circle(surface, petal_outer, (int(px), int(py)), radius)
        pygame.draw.circle(surface, petal_inner, (int((x + px) / 2), int((y + py) / 2)), max(2, int(4 * scale)))

    pygame.draw.circle(surface, (255, 252, 247), (int(x), int(y)), max(4, int(8 * scale)))

def draw_daisy(surface, x, y, scale, curve=0):
    draw_curved_stem(surface, x, y, scale, curve)
    pygame.draw.ellipse(surface, (78, 164, 84), (x - 15 * scale, y + 18 * scale, 16 * scale, 8 * scale))
    pygame.draw.ellipse(surface, (78, 164, 84), (x + 2 * scale, y + 25 * scale, 16 * scale, 8 * scale))

    ring = 18 * scale
    petal_w = 9 * scale
    petal_h = 18 * scale

    for angle in range(0, 360, 24):
        px = x + math.cos(math.radians(angle)) * ring
        py = y + math.sin(math.radians(angle)) * ring
        rect = pygame.Rect(0, 0, max(4, int(petal_w)), max(8, int(petal_h)))
        rect.center = (int(px), int(py))
        pygame.draw.ellipse(surface, (255, 255, 255), rect)

    pygame.draw.circle(surface, (238, 196, 58), (int(x), int(y)), max(5, int(10 * scale)))
    pygame.draw.circle(surface, (248, 222, 100), (int(x - 2 * scale), int(y - 2 * scale)), max(2, int(4 * scale)))

def draw_rose(surface, x, y, scale, curve=0):
    draw_curved_stem(surface, x, y, scale, curve)
    pygame.draw.ellipse(surface, (76, 152, 78), (x - 15 * scale, y + 19 * scale, 16 * scale, 9 * scale))
    pygame.draw.ellipse(surface, (76, 152, 78), (x + 2 * scale, y + 26 * scale, 18 * scale, 9 * scale))

    outer = (184, 28, 63)
    mid = (160, 18, 54)
    inner = (124, 10, 42)
    glow = (220, 86, 116)

    pygame.draw.circle(surface, outer, (int(x), int(y)), max(7, int(16 * scale)))
    pygame.draw.circle(surface, mid, (int(x - 4 * scale), int(y + 1 * scale)), max(5, int(12 * scale)))
    pygame.draw.circle(surface, mid, (int(x + 4 * scale), int(y - 2 * scale)), max(4, int(10 * scale)))
    pygame.draw.circle(surface, inner, (int(x), int(y)), max(3, int(7 * scale)))
    pygame.draw.arc(surface, glow, (x - 9 * scale, y - 9 * scale, 18 * scale, 18 * scale), 0.2, 3.8, 2)

def draw_tulip(surface, x, y, scale, curve=0):
    draw_curved_stem(surface, x, y, scale, curve)
    pygame.draw.ellipse(surface, (82, 165, 90), (x - 16 * scale, y + 21 * scale, 18 * scale, 9 * scale))
    pygame.draw.ellipse(surface, (82, 165, 90), (x + 1 * scale, y + 28 * scale, 20 * scale, 9 * scale))

    petal_dark = (176, 54, 94)
    petal_mid = (222, 103, 140)
    petal_light = (246, 159, 186)

    pygame.draw.ellipse(surface, petal_dark, (x - 14 * scale, y - 12 * scale, 28 * scale, 28 * scale))
    pygame.draw.ellipse(surface, petal_mid, (x - 11 * scale, y - 10 * scale, 22 * scale, 25 * scale))
    pygame.draw.ellipse(surface, petal_light, (x - 4 * scale, y - 7 * scale, 8 * scale, 18 * scale))

    pygame.draw.polygon(surface, petal_mid, [
        (x - 14 * scale, y + 2 * scale),
        (x - 6 * scale, y - 14 * scale),
        (x, y + 2 * scale)
    ])
    pygame.draw.polygon(surface, petal_mid, [
        (x, y + 2 * scale),
        (x + 6 * scale, y - 14 * scale),
        (x + 14 * scale, y + 2 * scale)
    ])

def draw_forget_me_not(surface, x, y, scale, curve=0):
    draw_curved_stem(surface, x, y, scale, curve)
    pygame.draw.ellipse(surface, (84, 167, 90), (x - 14 * scale, y + 17 * scale, 15 * scale, 8 * scale))
    pygame.draw.ellipse(surface, (84, 167, 90), (x + 2 * scale, y + 24 * scale, 15 * scale, 8 * scale))

    petal_color = (123, 159, 255)
    center_color = (255, 220, 86)

    cluster_offsets = [(-11, -9), (8, -11), (-1, 4), (14, 6)]
    for ox, oy in cluster_offsets:
        cx = x + ox * scale
        cy = y + oy * scale

        for angle in range(0, 360, 72):
            px = cx + math.cos(math.radians(angle)) * (6 * scale)
            py = cy + math.sin(math.radians(angle)) * (6 * scale)
            pygame.draw.circle(surface, petal_color, (int(px), int(py)), max(2, int(4 * scale)))

        pygame.draw.circle(surface, center_color, (int(cx), int(cy)), max(2, int(2 * scale)))

def bouquet_flower_positions(n):
    rows = [
        [(-48, -118), (-20, -145), (10, -128), (38, -150)],
        [(-58, -92), (-28, -110), (5, -100), (34, -114), (62, -98)],
        [(-42, -62), (-10, -74), (20, -68), (48, -76)]
    ]
    flat = []
    for row in rows:
        flat.extend(row)
    return flat[:n]

def draw_bouquet_wrap(surface):
    base_x = 1110
    base_y = 610

    pygame.draw.polygon(surface, (228, 198, 170), [
        (base_x - 82, base_y - 36),
        (base_x + 74, base_y - 22),
        (base_x + 25, base_y + 118),
        (base_x - 20, base_y + 118),
    ])

    pygame.draw.polygon(surface, (245, 224, 205), [
        (base_x - 88, base_y - 40),
        (base_x - 20, base_y - 100),
        (base_x + 6, base_y + 8),
    ])

    pygame.draw.polygon(surface, (238, 214, 192), [
        (base_x + 78, base_y - 24),
        (base_x + 26, base_y - 108),
        (base_x + 10, base_y + 8),
    ])

    pygame.draw.rect(surface, (213, 166, 176), (base_x - 15, base_y + 45, 30, 72), border_radius=10)
    pygame.draw.ellipse(surface, (198, 136, 151), (base_x - 36, base_y + 52, 28, 16))
    pygame.draw.ellipse(surface, (198, 136, 151), (base_x + 8, base_y + 52, 28, 16))

def draw_bouquet(surface):
    base_x = 1110
    base_y = 610
    shown = bouquet[-12:]
    positions = bouquet_flower_positions(len(shown))

    for flower_type, (dx, dy) in zip(shown, positions):
        x = base_x + dx
        y = base_y + dy
        scale = 0.68

        if flower_type == "frangipani":
            draw_frangipani(surface, x, y, scale, curve=random.uniform(-3, 3))
        elif flower_type == "daisy":
            draw_daisy(surface, x, y, scale, curve=random.uniform(-3, 3))
        elif flower_type == "rose":
            draw_rose(surface, x, y, scale, curve=random.uniform(-3, 3))
        elif flower_type == "tulip":
            draw_tulip(surface, x, y, scale, curve=random.uniform(-3, 3))
        elif flower_type == "forget_me_not":
            draw_forget_me_not(surface, x, y, scale, curve=random.uniform(-3, 3))

    draw_bouquet_wrap(surface)

def update_clouds():
    for cloud in clouds:
        cloud["x"] += cloud["speed"]
        if cloud["x"] > GARDEN_WIDTH + 140:
            cloud["x"] = -220
            cloud["y"] = random.randint(45, 180)

running = True
while running:
    t = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if ser.in_waiting:
        msg = ser.readline().decode("utf-8", errors="ignore").strip()
        if msg:
            print("Received:", msg)

        if msg == "MODE:PLANT":
            current_mode = "PLANT"
        elif msg == "MODE:WATER":
            current_mode = "WATER"
        elif msg == "MODE:CUT":
            current_mode = "CUT"
        elif msg == "RESET":
            flowers.clear()
            bouquet.clear()
            petals.clear()
            drops.clear()
            sparkles.clear()
            current_mode = "PLANT"
        elif msg == "FLOWER:FRANGIPANI":
            handle_flower_touch("frangipani")
        elif msg == "FLOWER:DAISY":
            handle_flower_touch("daisy")
        elif msg == "FLOWER:ROSE":
            handle_flower_touch("rose")
        elif msg == "FLOWER:TULIP":
            handle_flower_touch("tulip")
        elif msg == "FLOWER:FORGET_ME_NOT":
            handle_flower_touch("forget_me_not")

    update_clouds()

    for petal in petals[:]:
        petal.update()
        if petal.life <= 0:
            petals.remove(petal)

    for drop in drops[:]:
        drop.update()
        if drop.done:
            drops.remove(drop)

    for sparkle in sparkles[:]:
        sparkle.update()
        if sparkle.life <= 0:
            sparkles.remove(sparkle)

    draw_background(screen)

    project_title = title_font.render("Bloomscape", True, TEXT_MAIN)
    project_subtitle = subtitle_font.render("grow, water, gather", True, TEXT_SUB)
    screen.blit(project_title, (26, 20))
    screen.blit(project_subtitle, (32, 76))

    for flower in flowers:
        flower.draw(screen, t)

    for petal in petals:
        petal.draw(screen)

    for drop in drops:
        drop.draw(screen)

    for sparkle in sparkles:
        sparkle.draw(screen)

    draw_bouquet(screen)

    pygame.display.flip()
    clock.tick(60)

ser.close()
pygame.quit()
