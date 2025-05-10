import pygame
import sys
import os
import random

pygame.init()
WIDTH, HEIGHT = 928, 512
FPS = 60
TITLE = "Joyeux Anniversaire les petits indiens"
ASSET_DIR = r"C:\Users\Malkai\Desktop\Streaming\Images"
FONT = pygame.font.SysFont("comicsansms", 38)
FONT_SMALL = pygame.font.SysFont("comicsansms", 26)

def load_img(name, scale=None, colorkey=None):
    path = os.path.join(ASSET_DIR, name)
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    if colorkey is not None:
        img.set_colorkey(colorkey)
    return img

def play_music(filename, volume=0.5, loop=-1):
    path = os.path.join(ASSET_DIR, filename)
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loop)

def play_sound(name, volume=0.5):
    path = os.path.join(ASSET_DIR, name)
    snd = pygame.mixer.Sound(path)
    snd.set_volume(volume)
    snd.play()

def cut_sheet(sheet, frame_width=64, frame_height=64):
    frames = []
    sw, sh = sheet.get_size()
    for y in range(0, sh // frame_height):
        for x in range(0, sw // frame_width):
            frame = sheet.subsurface((x * frame_width, y * frame_height, frame_width, frame_height))
            frames.append(frame)
    return frames

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

bg1 = load_img('background1.png', (WIDTH, HEIGHT))
bg2 = load_img('background2.png', (WIDTH, HEIGHT))
khezu_img = load_img('KhezuL.png', (110, 92))
indian_img = load_img('Pweto.png', (70, 70))
cake_img = load_img('tigre desssin.png', (80, 72))
confetti = load_img('BLcheers.gif', (64, 64))
monster_img = load_img('ksekos.png', (68, 68))
effect_sheet = load_img('effetanim16.png')
effect_frames = cut_sheet(effect_sheet)

bg_music = 'Piano relaxant2.mp3'
win_music = 'The moment.mp3'
lose_music = 'schling2.mp3'
snd_collect = 'schling.mp3'

class Cake(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = cake_img
        self.rect = self.image.get_rect(topleft=(x, y))
    def update(self):
        pass

class Effect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = effect_frames
        self.cur = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.done = False
    def update(self):
        self.cur += 0.5
        if self.cur >= len(self.frames):
            self.done = True
            return
        self.image = self.frames[int(self.cur)]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = indian_img
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-10))
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 7
        self.jump_power = -14
        self.on_ground = True
    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.velocity.y += 0.75
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity.y = self.jump_power
            self.on_ground = False
        self.rect.y += int(self.velocity.y)
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
            self.velocity.y = 0
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)

class Monster(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = khezu_img
        self.rect = self.image.get_rect(midtop=(random.randint(60, WIDTH-60), -90))
        self.speed = random.uniform(2.0, 3.7)
        self.direction = random.choice([-1,1])
    def update(self):
        self.rect.x += self.direction * 2
        self.rect.y += self.speed
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1
        if self.rect.top > HEIGHT + 10:
            self.kill()

class FakeMonster(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = monster_img
        self.rect = self.image.get_rect(midtop=(random.randint(60, WIDTH-60), -68))
        self.speed = random.uniform(1.1, 2.4)
        self.direction = random.choice([-1,1])
    def update(self):
        self.rect.x += self.direction
        self.rect.y += self.speed
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1
        if self.rect.top > HEIGHT + 10:
            self.kill()

def draw_birthday_banner():
    t0 = FONT.render("Joyeux Anniversaire", True, (255, 210, 60))
    t1 = FONT_SMALL.render("Ramasse tous les gâteaux avant que Khezu ne t'attrape!", True, (40, 240, 220))
    t2 = FONT_SMALL.render("(Espace pour sauter, ← → pour bouger)", True, (255, 210, 120))
    screen.blit(t0, (WIDTH//2 - t0.get_width()//2, 12))
    screen.blit(t1, (WIDTH//2 - t1.get_width()//2, 48))
    screen.blit(t2, (WIDTH//2 - t2.get_width()//2, 92))

def show_credits(win):
    screen.fill((20,0,50))
    color = (255,230,100) if win else (255,0,0)
    ms = "Bravo, tu as fêté l'anniversaire !" if win else "Khezu a tout mangé !"
    msc = FONT.render(ms, True, color)
    screen.blit(msc, (WIDTH//2 - msc.get_width()//2, 100))
    cr = FONT_SMALL.render("code: tchat  |  art: ansimuz, BDragon1727", True, (200, 200, 245))
    screen.blit(cr, (WIDTH//2 - cr.get_width()//2, 320))
    pygame.display.flip()
    pygame.time.wait(4000)

def main():
    print("Longue vie à Khezu le best monstre !")
    play_music(bg_music, volume=0.5)
    clock = pygame.time.Clock()
    backgs = [bg1, bg2]
    bg_idx = 0
    player = Player()
    cakes = pygame.sprite.Group()
    monsters = pygame.sprite.Group()
    fakemons = pygame.sprite.Group()
    effects = pygame.sprite.Group()
    for i in range(10):
        x, y = random.randint(80, WIDTH-80), random.randint(170, HEIGHT-110)
        cakes.add(Cake(x, y))
    start_ticks = pygame.time.get_ticks()
    elapsed = 0
    running = True
    lose = False
    win = False
    cake_collected = 0
    confetti_timer = 0
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); # NENON PAS BIEN : sys.exit()
        keys = pygame.key.get_pressed()
        screen.blit(backgs[bg_idx], (0,0))
        draw_birthday_banner()
        player.update(keys)
        cakes.update()
        monsters.update()
        fakemons.update()
        effects.update()

        cakes.draw(screen)
        monsters.draw(screen)
        fakemons.draw(screen)
        screen.blit(player.image, player.rect)
        for ef in list(effects):
            ef.update()
            if ef.done:
                effects.remove(ef)
            else:
                screen.blit(ef.image, ef.rect)

        got_cake = pygame.sprite.spritecollide(player, cakes, True)
        if got_cake:
            for c in got_cake:
                play_sound(snd_collect, 0.32)
                effects.add(Effect(c.rect.centerx, c.rect.centery))
                cake_collected += 1

        if random.random() < 0.018:
            monsters.add(Monster())
        if random.random() < 0.01:
            fakemons.add(FakeMonster())

        scoretxt = FONT_SMALL.render(f"Gâteaux: {cake_collected}/{10}", True, (220,235,230))
        screen.blit(scoretxt, (24,18))

        hit_monster = pygame.sprite.spritecollide(player, monsters, False)
        elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
        if hit_monster:
            lose = True
            play_sound(lose_music, 0.5)
            break
        if cake_collected == 10:
            win = True
            play_music(win_music, 0.52, loop=0)
            break

        if int(elapsed) % 7 == 0:
            bg_idx = 1
        else:
            bg_idx = 0

        if cake_collected >= 8 and confetti_timer % 6 == 0:
            x = random.randint(32, WIDTH-32)
            y = random.randint(32, HEIGHT-32)
            screen.blit(confetti, (x, y))
        confetti_timer += 1
        pygame.display.flip()

    pygame.mixer.music.stop()
    show_credits(win)

while True:
    main()