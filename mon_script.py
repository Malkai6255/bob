import pygame
import sys
import os
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

os.environ['SDL_VIDEO_CENTERED'] = '1'
WIDTH, HEIGHT = 800, 600
FPS = 60

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khezu City Dash")

IMG_DIR = r"C:\Users\Malkai\Desktop\Streaming\Images"

def load_img(name, colorkey=None):
    img = pygame.image.load(os.path.join(IMG_DIR, name)).convert_alpha()
    if colorkey: img.set_colorkey(colorkey)
    return img

def load_sheet(name):
    img = load_img(name)
    frames = []
    for y in range(0, img.get_height(), 64):
        for x in range(0, img.get_width(), 64):
            rect = pygame.Rect(x, y, 64, 64)
            frames.append(img.subsurface(rect).copy())
    return frames

bg1 = load_img("background1.png")
bg2 = load_img("background2.png")
player_img = load_img("toonlink-link.gif")
khezu_img = load_img("KhezuL.png")
pweto_img = load_img("Pweto.png")
tigre_img = load_img("tigre desssin.png")
colere_img = load_img("colere.png")

sheet_fx = load_sheet("effetanim03.png")

pygame.mixer.music.load(os.path.join(IMG_DIR, "cyberpunk-street.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

schling = pygame.mixer.Sound(os.path.join(IMG_DIR, "schling.mp3"))
schling.set_volume(0.5)
lose_sound = pygame.mixer.Sound(os.path.join(IMG_DIR, "schling2.mp3"))
lose_sound.set_volume(0.5)
win_sound = pygame.mixer.Sound(os.path.join(IMG_DIR, "Piano relaxant3.mp3"))
win_sound.set_volume(0.5)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 32)
bigfont = pygame.font.SysFont("Consolas", 72)

class ParallaxBG:
    def __init__(self, img, speed):
        self.img = img
        self.x1 = 0
        self.x2 = img.get_width()
        self.speed = speed
    def update(self):
        self.x1 -= self.speed
        self.x2 -= self.speed
        if self.x1 <= -self.img.get_width():
            self.x1 = self.x2 + self.img.get_width()
        if self.x2 <= -self.img.get_width():
            self.x2 = self.x1 + self.img.get_width()
    def draw(self, surface):
        surface.blit(self.img, (self.x1, 0))
        surface.blit(self.img, (self.x2, 0))

class Platform:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
    def update(self):
        self.rect.x -= self.speed
    def draw(self, surface):
        pygame.draw.rect(surface, (50, 150, 50), self.rect)
    def offscreen(self):
        return self.rect.right < 0

class Player:
    def __init__(self):
        self.img = player_img
        self.rect = self.img.get_rect(center=(100, HEIGHT//2 - 100))
        self.vel = 0
        self.gravity = 0.7
        self.jump_str = -12
        self.on_ground = False
        self.mask = pygame.mask.from_surface(self.img)
        self.invincible = 0
    def update(self, keys, platforms):
        self.vel += self.gravity
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if self.on_ground:
                self.vel = self.jump_str
                schling.play()
        self.rect.y += int(self.vel)
        self.on_ground = False
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel = 0
            self.on_ground = True
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel = 0
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel > 0: # falling
                    self.rect.bottom = plat.rect.top
                    self.vel = 0
                    self.on_ground = True
        if self.invincible: self.invincible -= 1
    def draw(self, surface):
        if self.invincible and (pygame.time.get_ticks()//100)%2:
            return
        surface.blit(self.img, self.rect.topleft)

class Obstacle:
    def __init__(self, img, speed, y=None):
        self.img = img
        self.speed = speed
        self.rect = self.img.get_rect()
        self.rect.x = WIDTH + random.randint(0, 200)
        self.rect.y = y if y is not None else random.randint(50, HEIGHT-64)
        self.mask = pygame.mask.from_surface(self.img)
        self.kind = random.choice(["khezu", "pweto", "tigre", "colere"])
    def update(self):
        self.rect.x -= self.speed
    def draw(self, surface):
        surface.blit(self.img, self.rect.topleft)
    def offscreen(self):
        return self.rect.right < 0

class Effect:
    def __init__(self, x, y):
        self.frames = sheet_fx
        self.idx = 0
        self.rect = self.frames[0].get_rect(center=(x, y))
        self.done = False
    def update(self):
        self.idx += 1
        if self.idx >= len(self.frames):
            self.done = True
    def draw(self, surface):
        if not self.done:
            surface.blit(self.frames[self.idx%len(self.frames)], self.rect.topleft)

bg_layers = [
    ParallaxBG(bg1, 3),
    ParallaxBG(bg2, 1)
]

player = Player()
obstacles = []
effects = []
platforms = []

score = 0
highscore = 0
game_over = False
win_game = False

def make_obstacle():
    img = random.choice([khezu_img, pweto_img, tigre_img, colere_img])
    return Obstacle(img, 7, None)

def make_platform():
    x = WIDTH + random.randint(0, 200)
    y = random.randint(200, HEIGHT - 100)
    return Platform(x, y, random.randint(100, 300), 20, 3)

def reset():
    global player, obstacles, effects, score, game_over, win_game, platforms
    player = Player()
    obstacles.clear()
    effects.clear()
    platforms.clear()
    score = 0
    game_over = False
    win_game = False

def game_credits(win):
    win.fill((0,0,0))
    if win:
        txt = bigfont.render("BRAVO !", 1, (255,255,0))
    else:
        txt = bigfont.render("PERDU !", 1, (255,50,50))
    win.blit(txt, (WIDTH//2-txt.get_width()//2, 100))
    lines = [
        "Merci d'avoir joué !",
        "Code par tchat",
        "Art par ansimuz, BDragon1727",
        "Khezu est dans tous nos cœurs.",
        f"Score: {score}",
        f"Highscore: {highscore}",
        "Espace: rejouer    Echap: quitter"
    ]
    for i,l in enumerate(lines):
        ff = font.render(l,1,(230,230,230))
        win.blit(ff, (WIDTH//2-ff.get_width()//2, 240+40*i))
    pygame.display.flip()

print("Khezu power! Let's go.")
obstacles.append(make_obstacle())
platforms.append(make_platform())
SPAWN_OBSTACLE = pygame.USEREVENT+1
SPAWN_PLATFORM = pygame.USEREVENT+2
pygame.time.set_timer(SPAWN_OBSTACLE, 1100)
pygame.time.set_timer(SPAWN_PLATFORM, 2000)

while True:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()
    if not game_over and not win_game:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit(); # NENON PAS BIEN : sys.exit()
            if ev.type == SPAWN_OBSTACLE:
                obstacles.append(make_obstacle())
            if ev.type == SPAWN_PLATFORM:
                platforms.append(make_platform())
        for bg in bg_layers:
            bg.update()
        player.update(keys, platforms)
        for ob in obstacles:
            ob.update()
        for fx in effects:
            fx.update()
        effects = [f for f in effects if not f.done]
        obstacles = [o for o in obstacles if not o.offscreen()]
        platforms = [p for p in platforms if not p.offscreen()]
        for ob in obstacles:
            if player.rect.colliderect(ob.rect):
                offset = (ob.rect.x-player.rect.x, ob.rect.y-player.rect.y)
                if player.mask.overlap(ob.mask, offset) and player.invincible==0:
                    effects.append(Effect(player.rect.centerx, player.rect.centery))
                    lose_sound.play()
                    game_over = True
                    if score>highscore: highscore=score
        if score>=30:
            win_sound.play()
            win_game = True
            if score>highscore: highscore=score
        for ob in obstacles:
            if ob.rect.right < player.rect.left and getattr(ob, "counted", False) is False:
                score += 1
                ob.counted = True
        for bg in bg_layers[::-1]:
            bg.draw(win)
        for plat in platforms:
            plat.draw(win)
        player.draw(win)
        for ob in obstacles:
            ob.draw(win)
        for fx in effects:
            fx.draw(win)
        srf = font.render(f"Score: {score}",1,(240,240,240))
        win.blit(srf, (20,20))
        if score>highscore:
            highscore = score
        hrf = font.render(f"Highscore: {highscore}",1,(200,200,65))
        win.blit(hrf, (20,60))
        pygame.display.flip()
        win.fill((10,10,30))
    else:
        game_credits(win_game)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); # NENON PAS BIEN : sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    reset()
                    pygame.mixer.music.play(-1)
                elif ev.key == pygame.K_ESCAPE:
                    pygame.quit(); # NENON PAS BIEN : sys.exit()