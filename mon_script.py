import pygame
import random
import os
import sys

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khezu Jump")
clock = pygame.time.Clock()
FPS = 60

ASSET_PATH = r"C:\Users\Malkai\Desktop\Streaming\Images"

def load_img(name, colorkey=None):
    img = pygame.image.load(os.path.join(ASSET_PATH, name)).convert_alpha()
    if colorkey is not None:
        img.set_colorkey(colorkey)
    return img

def load_sound(name, volume=0.5):
    s = pygame.mixer.Sound(os.path.join(ASSET_PATH, name))
    s.set_volume(volume)
    return s

background_img = load_img('background1.png')
background_img2 = load_img('background2.png')
player_imgs = [load_img('toonlink-link.gif')]
platform_img = load_img('Pweto.png')
monster_img = load_img('KhezuL.png')
credit_img = pygame.transform.scale(load_img('colere.png'), (WIDTH, HEIGHT // 2))

music_files = ['Piano relaxant3.mp3', 'cyberpunk-street.mp3', 'Piano relaxant2.mp3', 'The moment.mp3']
pygame.mixer.music.load(os.path.join(ASSET_PATH, random.choice(music_files)))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

jump_sfx = load_sound('schling.mp3', 0.5)
lose_sfx = load_sound('schling2.mp3', 0.5)

FONT = pygame.font.SysFont("consolas", 24, bold=True)
BIGFONT = pygame.font.SysFont("consolas", 48, bold=True)

def draw_text(s, size, color, x, y, mid=True, shadow=True):
    font = pygame.font.SysFont("consolas", size, bold=True)
    img = font.render(s, True, (20,20,20) if shadow else color)
    if mid:
        rect = img.get_rect(center=(x, y))
        if shadow:
            screen.blit(img, rect.move(2,2))
            img2 = font.render(s, True, color)
            screen.blit(img2, rect)
        else:
            screen.blit(img, rect)
    else:
        screen.blit(img, (x,y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = player_imgs
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.x_speed = 0
        self.y_speed = 0
        self.score = 0
        self.max_height = self.rect.top
        self.jump_power = -14
        self.alive = True
        self.khezu_power = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_speed -= 0.7
            if self.x_speed < -7: self.x_speed = -7
        elif keys[pygame.K_RIGHT]:
            self.x_speed += 0.7
            if self.x_speed > 7: self.x_speed = 7
        else:
            self.x_speed *= 0.85
            if abs(self.x_speed) < 0.5: self.x_speed = 0
        self.rect.x += int(self.x_speed)
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH

        self.y_speed += 0.6
        if self.y_speed > 18: self.y_speed = 18
        self.rect.y += int(self.y_speed)

        if self.rect.top < self.max_height:
            self.score += self.max_height - self.rect.top
            self.max_height = self.rect.top

        if self.rect.top > HEIGHT+40:
            self.alive = False

    def jump(self):
        self.y_speed = self.jump_power
        jump_sfx.play()

    def draw(self, surf):
        surf.blit(self.image, self.rect)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, breakable=False, monster=False):
        pygame.sprite.Sprite.__init__(self)
        w = platform_img.get_width()
        self.image = platform_img.copy()
        if monster:
            p = monster_img
            self.image = pygame.Surface((w,48), pygame.SRCALPHA)
            self.image.blit(platform_img, (0, 24))
            self.image.blit(p, (w//2-p.get_width()//2, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.breakable = breakable
        self.monster = monster
        self.broken = False

    def update(self, camera_scroll):
        self.rect.y += camera_scroll
        if self.rect.top > HEIGHT+20:
            self.kill()

    def draw(self, surf):
        surf.blit(self.image, self.rect)

def make_platform_group(starty, num=8):
    group = pygame.sprite.Group()
    y = starty
    for _ in range(num):
        x = random.randint(10, WIDTH-80)
        breakable = random.random() < 0.13
        monster = random.random() < 0.12
        if monster:
            pf = Platform(x, y, monster=True)
        else:
            pf = Platform(x, y, breakable=breakable)
        group.add(pf)
        y -= random.randint(58, 110)
    return group

player = Player()
platforms = make_platform_group(HEIGHT-50, 8)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
for p in platforms:
    all_sprites.add(p)

background_scroll = 0
cam_scroll = 0
bg_y, bg2_y = 0, -background_img.get_height()

def run_game():
    global platforms, all_sprites, cam_scroll, background_scroll, bg_y, bg2_y, player
    running = True
    game_over = False
    win = False
    timer = 0
    while running:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                # NENON PAS BIEN : sys.exit()
            if not game_over:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    if player.y_speed > 0:
                        for plat in platforms:
                            if player.rect.bottom <= plat.rect.top+8 and \
                               player.rect.right >= plat.rect.left+15 and \
                               player.rect.left <= plat.rect.right-15 and \
                               plat.rect.top-player.rect.bottom<22 and not plat.broken:
                                if plat.monster:
                                    print("Le Khezu apparaît! KHEZU 4EVER.")
                                    lose_sfx.play()
                                    player.alive = False
                                elif plat.breakable:
                                    plat.broken = True
                                    all_sprites.remove(plat)
                                    platforms.remove(plat)
                                else:
                                    player.jump()
                                break

        if not game_over:
            if player.rect.top <= HEIGHT//3:
                cam_scroll = int((HEIGHT//3-player.rect.top)*0.46)
            else:
                cam_scroll = 0

            bg_step = cam_scroll
            bg_y += bg_step
            bg2_y += bg_step
            if bg_y >= HEIGHT:
                bg_y = bg2_y - background_img.get_height()
            if bg2_y >= HEIGHT:
                bg2_y = bg_y - background_img2.get_height()
            screen.blit(background_img, (0, bg_y))
            screen.blit(background_img2, (0, bg2_y))

            all_sprites.update(cam_scroll)
            for p in platforms:
                if p.broken:
                    continue
                if player.y_speed > 0:
                    if player.rect.bottom <= p.rect.top+8 and \
                        player.rect.centerx >= p.rect.left+10 and \
                        player.rect.centerx <= p.rect.right-10 and \
                        p.rect.top-player.rect.bottom < 21:
                        if p.monster:
                            print("Le Khezu te regarde. KHEZU ROOLZ")
                            lose_sfx.play()
                            player.alive = False
                        elif p.breakable:
                            p.broken = True
                            all_sprites.remove(p)
                            platforms.remove(p)
                        else:
                            player.jump()
                p.draw(screen)
            player.draw(screen)

            if player.score > 2400:
                game_over = True
                win = True
                timer = pygame.time.get_ticks()
            if not player.alive:
                game_over = True
                timer = pygame.time.get_ticks()

            draw_text(f"SCORE : {player.score//10}", 26, (255,255,255), WIDTH//2, 36)
        else:
            screen.fill((14,18,44))
            if win:
                draw_text("VICTOIRE!", 56, (255,220,0), WIDTH//2, HEIGHT//2-86)
            else:
                draw_text("PERDU!", 56, (255,10,10), WIDTH//2, HEIGHT//2-86)
            screen.blit(credit_img, (0, HEIGHT//2-20))
            draw_text("CODE: tchat", 26, (240,240,220), WIDTH//2, HEIGHT//2+86)
            draw_text("ART: ansimuz, BDragon1727", 24, (200,240,220), WIDTH//2, HEIGHT//2+140)
            draw_text("Press [R] pour rejouer ou [ESC] quitter", 20, (255,255,255), WIDTH//2, HEIGHT-40)

            if pygame.time.get_ticks()-timer > 900:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    print("KHEZU DOMINATOR. Encore une partie.")
                    player = Player()
                    platforms = make_platform_group(HEIGHT-50, 8)
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(player)
                    for p in platforms:
                        all_sprites.add(p)
                    background_y = 0
                    game_over = False
                    win = False
                    bg_y, bg2_y = 0, -background_img.get_height()
                if keys[pygame.K_ESCAPE]:
                    pygame.quit(), # NENON PAS BIEN : sys.exit()
        pygame.display.flip()

run_game()