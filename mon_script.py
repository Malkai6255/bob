import pygame
import os
import random
from twitch import TwitchIRCClient

pygame.init()
WIDTH, HEIGHT = 960, 540
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khezu Shakira Showdown")
CLOCK = pygame.time.Clock()
FPS = 60

IMG_PATH = r"C:\Users\Malkai\Desktop\Streaming\Images"
BG_IMG1 = pygame.image.load(os.path.join(IMG_PATH, "background1.png")).convert()
BG_IMG2 = pygame.image.load(os.path.join(IMG_PATH, "background2.png")).convert()
KHEZU_IMG = pygame.image.load(os.path.join(IMG_PATH, "KhezuL.png")).convert_alpha()
SHAKIRA_IMG = pygame.image.load(os.path.join(IMG_PATH, "BLcheers.gif")).convert_alpha()
EFFECT_SHEET = pygame.image.load(os.path.join(IMG_PATH, "effetanim03.png")).convert_alpha()
FONT = pygame.font.SysFont("arial", 32, True)
BIGFONT = pygame.font.SysFont("arial", 56, True)

def blit_bg(wave):
    if wave % 2 == 0:
        WIN.blit(BG_IMG1, (0,0))
    else:
        WIN.blit(BG_IMG2, (0,0))

def load_effect_frames(sheet):
    frames = []
    for i in range(sheet.get_width() // 64):
        fr = pygame.Surface((64,64), pygame.SRCALPHA)
        fr.blit(sheet, (0,0), (i*64, 0, 64,64))
        frames.append(fr)
    return frames

def draw_text(surf, text, font, color, x, y, center=False):
    t = font.render(text, 1, color)
    if center:
        rect = t.get_rect(center=(x, y))
        surf.blit(t, rect)
    else:
        surf.blit(t, (x, y))

class Khezu(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = KHEZU_IMG
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 100))
        self.speed = 7
    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))

class ShakiraDrop(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = SHAKIRA_IMG
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH-50), -40))
        self.speed = random.randint(4,8)
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Effect(pygame.sprite.Sprite):
    def __init__(self, pos, frames):
        super().__init__()
        self.frames = frames
        self.index = 0
        self.image = frames[0]
        self.rect = self.image.get_rect(center=pos)
    def update(self):
        self.index += 0.6
        if self.index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.index)]

def spawn_shakira():
    drop = ShakiraDrop()
    shakira_sprites.add(drop)

def spawn_effect(pos):
    frames = load_effect_frames(EFFECT_SHEET)
    eff = Effect(pos, frames)
    effect_sprites.add(eff)

def reset_game():
    khezu.rect.center = (WIDTH//2, HEIGHT - 100)
    for s in shakira_sprites: s.kill()
    for e in effect_sprites: e.kill()

khezu = Khezu()
shakira_sprites = pygame.sprite.Group()
effect_sprites = pygame.sprite.Group()
score = 0
lives = 5
wave = 1
game_over = False
win = False
shakira_queued = False
client = TwitchIRCClient()

def on_twitch_message(data):
    global shakira_queued
    message = data.get("message","")
    if "shakira" in message.lower():
        shakira_queued = True

client.on("chat", on_twitch_message)
client.start_background()

pygame.mixer.music.load(os.path.join(IMG_PATH, "cyberpunk-street.mp3"))
pygame.mixer.music.play(-1)

intro = True
while intro:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            client.stop()
            exit()
        elif event.type == pygame.KEYDOWN:
            intro = False
    WIN.blit(BG_IMG1, (0,0))
    draw_text(WIN, "Khezu & Shakira Showdown", BIGFONT, (255,50,50), WIDTH//2, HEIGHT//3, center=True)
    draw_text(WIN, "Déplace Khezu avec ← →   |  Interagis via Twitch chat: shakira", FONT, (255,255,255), WIDTH//2, HEIGHT//2, center=True)
    draw_text(WIN, "Appuie sur n'importe quelle touche pour commencer!", FONT, (255,255,0), WIDTH//2, HEIGHT*3//4, center=True)
    pygame.display.update()
    CLOCK.tick(30)

TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER, 1700)
running = True
while running:
    CLOCK.tick(FPS)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            client.stop()
        if event.type == TIMER and not game_over:
            if random.random() < 0.5:
                spawn_shakira()
    if shakira_queued and not game_over:
        spawn_shakira()
        shakira_queued = False
    if not game_over:
        khezu.update(keys)
        shakira_sprites.update()
        effect_sprites.update()
        
        hits = pygame.sprite.spritecollide(khezu, shakira_sprites, True)
        for h in hits:
            spawn_effect(khezu.rect.center)
            score += 1
            print("Khezu est satisfait d'avoir attrapé la Shakira !")
        for s in list(shakira_sprites):
            if s.rect.top > HEIGHT:
                s.kill()
                lives -= 1
                print("Khezu a laissé filer une Shakira... Il est triste !")
                if lives <= 0:
                    game_over = True
                    win = False
        if score >= 15:
            game_over = True
            win = True
            print("VICTOIRE ! KHEZU DOMINE LE MONDE ! SHAKIRA REINE !")
    blit_bg(wave)
    effect_sprites.draw(WIN)
    shakira_sprites.draw(WIN)
    WIN.blit(khezu.image, khezu.rect)
    draw_text(WIN, f"SCORE : {score}", FONT, (0,255,128), 28, 6)
    draw_text(WIN, f"VIES : {lives}", FONT, (255,0,0), WIDTH - 170, 6)
    pygame.display.update()
    if game_over:
        pygame.time.delay(1000)
        WIN.fill((0,0,0))
        if win:
            draw_text(WIN, "Khezu a remporté le Showdown !", BIGFONT, (200,255,80), WIDTH//2, HEIGHT//3, center=True)
            draw_text(WIN, "Bravo!", FONT, (255,255,255), WIDTH//2, HEIGHT//2, center=True)
        else:
            draw_text(WIN, "Khezu a échoué... (mais on aime Khezu)", BIGFONT, (220,100,100), WIDTH//2, HEIGHT//3, center=True)
            draw_text(WIN, "Retente ta chance sur le tchat Twitch !", FONT, (255,255,255), WIDTH//2, HEIGHT//2, center=True)
        draw_text(WIN, "Crédits:", FONT, (220,220,220), WIDTH//2, HEIGHT-120, center=True)
        draw_text(WIN, "Code par tchat", FONT, (255,255,200), WIDTH//2, HEIGHT-90, center=True)
        draw_text(WIN, "Art par ansimuz, BDragon1727", FONT, (100,255,255), WIDTH//2, HEIGHT-60, center=True)
        pygame.display.update()
        pygame.time.delay(4500)
        score = 0
        lives = 5
        wave += 1
        reset_game()
        game_over = False
        win = False

pygame.quit()
client.stop()