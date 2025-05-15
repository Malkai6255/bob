import pygame
import sys
import os
import random

# Constants
WIDTH, HEIGHT = 800, 480
GROUND = HEIGHT - 70
PLAYER_W, PLAYER_H = 48, 60
MUSH_W, MUSH_H = 64, 32
SPIKE_W, SPIKE_H = 40, 40
GRAVITY = 1.2
JUMP_PWR = 18
FPS = 60
GAME_DURATION = 60

IMGDIR = r"C:\Users\Malkai\Desktop\Streaming\Images"

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khezu Mushroom Escape")
clock = pygame.time.Clock()

bg_img1 = pygame.image.load(os.path.join(IMGDIR, "background1.png")).convert()
bg_img1 = pygame.transform.scale(bg_img1, (WIDTH, HEIGHT))
bg_img2 = pygame.image.load(os.path.join(IMGDIR, "background2.png")).convert()
bg_img2 = pygame.transform.scale(bg_img2, (WIDTH, HEIGHT))
bg_layers = [
    [bg_img1, 0],
    [bg_img2, 0]
]

def load_img(name, w=None, h=None, alpha=True):
    img = pygame.image.load(os.path.join(IMGDIR, name))
    if alpha:
        img = img.convert_alpha()
    else:
        img = img.convert()
    if w and h:
        img = pygame.transform.scale(img, (w, h))
    return img

player_imgs = [
    load_img("toonlink-link.gif", PLAYER_W, PLAYER_H),
    pygame.transform.flip(load_img("toonlink-link.gif", PLAYER_W, PLAYER_H), True, False)
]
khezu_img = load_img("KhezuL.png", 52, 52)
mush_img = load_img("Pweto.png", MUSH_W, MUSH_H)
spike_img = load_img("colere.png", SPIKE_W, SPIKE_H)
game_over_img = load_img("tigre desssin.png", 112, 112)
victory_img = load_img("BLcheers.gif", 112, 112)

pygame.mixer.music.load(os.path.join(IMGDIR, "cyberpunk-street.mp3"))
pygame.mixer.music.set_volume(0.5)
jump_sound = pygame.mixer.Sound(os.path.join(IMGDIR, "schling.mp3"))
jump_sound.set_volume(0.45)
hit_sound = pygame.mixer.Sound(os.path.join(IMGDIR, "schling2.mp3"))
hit_sound.set_volume(0.35)

def draw_text(s, x, y, size, col, f="arial", c=False):
    font = pygame.font.SysFont(f, size, bold=True)
    surf = font.render(s, True, col)
    rect = surf.get_rect()
    if c:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

def get_effect_frames(name):
    sheet = load_img(name)
    frames = []
    for i in range(0, sheet.get_width(), 64):
        frame = sheet.subsurface(pygame.Rect(i, 0, 64, 64))
        frames.append(frame.copy())
    return frames

effect_frames = get_effect_frames("effetanim23.png")

class EffectAnim(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.frames = effect_frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.index = 0
    def update(self):
        self.timer += 1
        if self.timer % 4 == 0:
            self.index += 1
            if self.index < len(self.frames):
                self.image = self.frames[self.index]
            else:
                self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_imgs[0]
        self.rect = pygame.Rect(110, GROUND-PLAYER_H, PLAYER_W, PLAYER_H)
        self.xv = 0
        self.yv = 0
        self.on_ground = False
        self.flip = False
        self.group = group
        self.anim_timer = 0
    def update(self, platforms):
        self.xv = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.xv = -6
            self.flip = True
        if keys[pygame.K_d]:
            self.xv = 6
            self.flip = False
        if keys[pygame.K_SPACE] and self.on_ground:
            self.yv = -JUMP_PWR
            self.on_ground = False
            jump_sound.play()
            print("Khezu ❤️ Jump")
            effect = EffectAnim(self.rect.centerx, self.rect.bottom)
            self.group.add(effect)
        self.yv += GRAVITY
        self.rect.x += self.xv
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        self.rect.y += int(self.yv)
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.yv > 0 and self.rect.bottom <= p.rect.bottom:
                    self.rect.bottom = p.rect.top
                    self.yv = 0
                    self.on_ground = True
        if self.rect.bottom > GROUND:
            self.rect.bottom = GROUND
            self.yv = 0
            self.on_ground = True
        self.anim_timer += 1
        self.image = player_imgs[int(self.flip)]

class Mushroom(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = mush_img
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.move_offset = random.randint(0, 99)
    def update(self):
        self.rect.y += int(2 * pygame.math.Vector2(0, pygame.math.sin(pygame.time.get_ticks() / 340 + self.move_offset)).y)
        if self.rect.top > HEIGHT + 10:
            self.kill()

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, mode='top'):
        pygame.sprite.Sprite.__init__(self)
        self.image = spike_img
        self.mode = mode
        self.rect = self.image.get_rect()
        if mode == 'top':
            self.rect.midtop = (x, y)
        else:
            self.rect.midbottom = (x, y)
        self.speed = random.randint(3, 8)
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((MUSH_W, MUSH_H), pygame.SRCALPHA)
        self.image.blit(mush_img, (0, 0))
        self.rect = self.image.get_rect(midbottom=(x, y))

def scroll_background(layers, speed):
    for i, (img, x) in enumerate(layers):
        new_x = x - speed//(i+2)
        if new_x <= -WIDTH:
            new_x = 0
        layers[i][1] = new_x
        screen.blit(img, (new_x, 0))
        screen.blit(img, (new_x + WIDTH, 0))

def main():
    pygame.mixer.music.play(-1)
    group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    spike_group = pygame.sprite.Group()
    player = Player(group)
    group.add(player)
    group.add(platform_group)
    score = 0
    mushroom_spawn_t = 70
    spike_spawn_t = 40
    t = 0
    running = True
    gameover = False
    win = False
    start_ticks = pygame.time.get_ticks()
    bg_scroll_amount = 2
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if not gameover:
            time_elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
            if time_elapsed >= GAME_DURATION:
                win = True
                gameover = True
                pygame.mixer.music.stop()
                pygame.time.wait(300)
                continue
            scroll_background(bg_layers, bg_scroll_amount)
            t += 1
            if t % mushroom_spawn_t == 0 or len(platform_group) < 4:
                x = random.randint(130, WIDTH-120)
                y = random.randint(170, GROUND-20)
                if all(abs(p.rect.centerx - x) > 100 for p in platform_group):
                    platform = Platform(x, y)
                    platform_group.add(platform)
                    group.add(platform)
            if t % spike_spawn_t == 0:
                x = WIDTH + random.randint(0, 40)
                y = GROUND - random.choice([0, 40, 80])
                s = Spike(x, y)
                spike_group.add(s)
                group.add(s)
            platform_group.update()
            spike_group.update()
            group.update(platform_group)
            for spike in spike_group:
                if player.rect.colliderect(spike.rect):
                    hit_sound.play()
                    effect = EffectAnim(player.rect.centerx, player.rect.centery)
                    group.add(effect)
                    gameover = True
                    win = False
                    pygame.mixer.music.stop()
                    pygame.time.wait(400)
            for plat in platform_group:
                if plat.rect.right < 0:
                    plat.kill()
            group.draw(screen)
            if (t // 20) % 3 == 0:
                screen.blit(khezu_img, (WIDTH-80, 38))
            draw_text("Temps: {}s".format(GAME_DURATION - time_elapsed), 20, 16, 26, (248,248,248))
            draw_text("Score: {}".format(time_elapsed*31), 20, 46, 22, (221,171,232))
            pygame.display.flip()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    main()
                    return
            screen.fill((24,20,28))
            scroll_background(bg_layers, 0)
            if win:
                screen.blit(victory_img, (WIDTH//2-56, HEIGHT//2-180))
                msg = "Ton lien avec Khezu t'a mené à la victoire!"
                draw_text(msg, WIDTH//2, HEIGHT//2-62, 30, (244,244,255), c=True)
                draw_text("Score: {}".format(GAME_DURATION*31), WIDTH//2, HEIGHT//2-22, 27, (183,232,221), c=True)
            else:
                screen.blit(game_over_img, (WIDTH//2-56, HEIGHT//2-170))
                draw_text("Écrasé par la colère des pics!", WIDTH//2, HEIGHT//2-60, 32, (255,70,70), c=True)
            draw_text("Espace ou toute touche pour rejouer", WIDTH//2, HEIGHT//2+48, 22, (222,255,255), c=True)
            draw_text("Crédits: code par tchat / art par ansimuz, BDragon1727", WIDTH//2, HEIGHT-34, 20, (242,232,210), c=True)
            pygame.display.flip()
    pygame.quit()
main()