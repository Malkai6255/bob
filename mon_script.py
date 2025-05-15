import pygame
import random
import os

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

def load_sound(name):
    s = pygame.mixer.Sound(os.path.join(ASSET_PATH, name))
    s.set_volume(0.5)
    return s

background_img = load_img('background1.png')
background_img2 = load_img('background2.png')
player_imgs = [load_img('toonlink-link.gif')]
platform_img = load_img('Pweto.png')
monster_img = load_img('KhezuL.png')
credit_img = pygame.transform.scale(load_img('colere.png'), (WIDTH, HEIGHT // 2))

music_files = ['Piano relaxant3.mp3', 'cyberpunk-street.mp3', 'Piano relaxant2.mp3', 'The moment.mp3']
pygame.mixer.music.load(os.path.join(ASSET_PATH, random.choice(music_files)))
pygame.mixer.music.play(-1)

jump_sfx = load_sound('schling.mp3')
lose_sfx = load_sound('schling2.mp3')

def draw_text(s, size, color, x, y, mid=True):
    font = pygame.font.SysFont("consolas", size, bold=True)
    img = font.render(s, True, color)
    if mid:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x,y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
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

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_speed = max(self.x_speed - 0.7, -7)
        elif keys[pygame.K_RIGHT]:
            self.x_speed = min(self.x_speed + 0.7, 7)
        else:
            self.x_speed *= 0.85
            if abs(self.x_speed) < 0.5: self.x_speed = 0
        self.rect.x += int(self.x_speed)
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))

        self.y_speed = min(self.y_speed + 0.6, 18)
        self.rect.y += int(self.y_speed)

        if self.rect.top < self.max_height:
            self.score += self.max_height - self.rect.top
            self.max_height = self.rect.top

        if self.rect.top > HEIGHT + 40:
            self.alive = False
    
    def jump(self):
        self.y_speed = self.jump_power
        jump_sfx.play()

    def draw(self, surf):
        surf.blit(self.image, self.rect)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, breakable=False, monster=False):
        super().__init__()
        self.image = platform_img.copy()
        if monster:
            self.image = pygame.Surface((platform_img.get_width(), 48), pygame.SRCALPHA)
            self.image.blit(platform_img, (0, 24))
            self.image.blit(monster_img, (platform_img.get_width() // 2 - monster_img.get_width() // 2, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.breakable = breakable
        self.monster = monster
        self.broken = False

    def update(self, camera_scroll):
        self.rect.y += camera_scroll
        if self.rect.top > HEIGHT + 20:
            self.kill()

    def draw(self, surf):
        surf.blit(self.image, self.rect)

def make_platform_group(starty, num=8):
    group = pygame.sprite.Group()
    y = starty
    for _ in range(num):
        x = random.randint(10, WIDTH - 80)
        monster = random.random() < 0.12
        breakable = not monster and random.random() < 0.13
        platform = Platform(x, y, breakable, monster)
        group.add(platform)
        y -= random.randint(58, 110)
    return group

player = Player()
platforms = make_platform_group(HEIGHT - 50, 8)
all_sprites = pygame.sprite.Group(player, *platforms)

bg_y, bg2_y = 0, -background_img.get_height()

def run_game():
    global platforms, all_sprites, bg_y, bg2_y, player
    running = True
    game_over = False
    win = False
    timer = 0
    while running:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        if not game_over:
            if player.rect.top <= HEIGHT // 3:
                cam_scroll = int((HEIGHT // 3 - player.rect.top) * 0.46)
            else:
                cam_scroll = 0

            bg_y += cam_scroll
            bg2_y += cam_scroll
            if bg_y >= HEIGHT:
                bg_y = bg2_y - background_img.get_height()
            if bg2_y >= HEIGHT:
                bg2_y = bg_y - background_img.get_height()
            screen.blit(background_img, (0, bg_y))
            screen.blit(background_img2, (0, bg2_y))

            all_sprites.update(cam_scroll)
            for p in platforms:
                if player.y_speed > 0 and player.rect.bottom <= p.rect.top + 8 and \
                        p.rect.centerx - 10 <= player.rect.centerx <= p.rect.right + 10 and \
                        abs(player.rect.bottom - p.rect.top) < 21 and not p.broken:
                    if p.monster:
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

            draw_text(f"SCORE: {player.score // 10}", 26, (255, 255, 255), WIDTH // 2, 36)
        else:
            screen.fill((14, 18, 44))
            if win:
                draw_text("VICTOIRE!", 56, (255, 220, 0), WIDTH // 2, HEIGHT // 2 - 86)
            else:
                draw_text("PERDU!", 56, (255, 10, 10), WIDTH // 2, HEIGHT // 2 - 86)
            screen.blit(credit_img, (0, HEIGHT // 2 - 20))
            draw_text("CODE: tchat", 26, (240, 240, 220), WIDTH // 2, HEIGHT // 2 + 86)
            draw_text("ART: ansimuz, BDragon1727", 24, (200, 240, 220), WIDTH // 2, HEIGHT // 2 + 140)
            draw_text("Press [R] pour rejouer ou [ESC] quitter", 20, (255, 255, 255), WIDTH // 2, HEIGHT - 40)

            if pygame.time.get_ticks() - timer > 900:
                if keys[pygame.K_r]:
                    player = Player()
                    platforms = make_platform_group(HEIGHT - 50, 8)
                    all_sprites = pygame.sprite.Group(player, *platforms)
                    bg_y, bg2_y = 0, -background_img.get_height()
                    game_over = False
                    win = False
        pygame.display.flip()

run_game()
pygame.quit()