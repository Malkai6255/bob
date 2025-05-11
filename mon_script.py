import pygame
import os
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
FPS = 60
FONT = pygame.font.SysFont("consolas", 28)
BIGFONT = pygame.font.SysFont("consolas", 46, True)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khezu Survival")

IMG_PATH = r"C:\Users\Malkai\Desktop\Streaming\Images"
BACKGROUND = pygame.image.load(os.path.join(IMG_PATH, "background1.png")).convert()
BACKGROUND2 = pygame.image.load(os.path.join(IMG_PATH, "background2.png")).convert()
KHEZU = pygame.image.load(os.path.join(IMG_PATH, "KhezuL.png")).convert_alpha()
PLAYER = pygame.image.load(os.path.join(IMG_PATH, "toonlink-link.gif")).convert_alpha()
HEART = pygame.image.load(os.path.join(IMG_PATH, "BLcheers.gif")).convert_alpha()
COLERE = pygame.image.load(os.path.join(IMG_PATH, "colere.png")).convert_alpha()

pygame.mixer.music.load(os.path.join(IMG_PATH, "cyberpunk-street.mp3"))
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)

SCHLING = pygame.mixer.Sound(os.path.join(IMG_PATH, "schling2.mp3"))
SCHLING.set_volume(0.5)

def blit_bg(bg, x):
    WINDOW.blit(bg, (x, 0))

def print_khezu():
    print("Khezu <3 oldschool power")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER
        self.rect = self.image.get_rect(center=(WIDTH//6, HEIGHT//2))
        self.speed = 5
        self.lives = 3
        self.shoot_cooldown = 0

    def update(self, keys):
        if keys[pygame.K_UP]: self.rect.y -= self.speed
        if keys[pygame.K_DOWN]: self.rect.y += self.speed
        if keys[pygame.K_LEFT]: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if keys[pygame.K_SPACE] and self.shoot_cooldown == 0:
            bullets.add(Bullet(self.rect.midright))
            self.shoot_cooldown = 15
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 8

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

class KhezuMonster(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = KHEZU
        self.rect = self.image.get_rect(midleft=(WIDTH + random.randint(0, 500), random.randint(20, HEIGHT-64)))
        self.speed = random.randint(3, 6)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.respawn()

    def respawn(self):
        self.rect.left = WIDTH + random.randint(0, 400)
        self.rect.y = random.randint(30, HEIGHT-64)
        self.speed = random.randint(3, 6)

class Effect(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = COLERE
        self.rect = self.image.get_rect(center=pos)
        self.timer = 24

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

def draw_hearts(lives):
    for i in range(lives):
        WINDOW.blit(HEART, (10 + i*32, 10))

def gameover_screen(result, score):
    pygame.mixer.music.stop()
    color = (200, 40, 40) if result == "perdu" else (40, 200, 120)
    WINDOW.fill((24, 24, 32))
    txt1 = BIGFONT.render("Khezu a eu raison de toi!" if result == "perdu" else "Tu as survécu!", 1, color)
    txt2 = FONT.render(f"Score : {score} sec", 1, (222, 222, 200))
    txt3 = FONT.render("code par tchat", 1, (200, 200, 255))
    txt4 = FONT.render("art par ansimuz, BDragon1727", 1, (150, 222, 255))
    WINDOW.blit(txt1, (WIDTH//2-txt1.get_width()//2, 120))
    WINDOW.blit(txt2, (WIDTH//2-txt2.get_width()//2, 180))
    WINDOW.blit(txt3, (WIDTH//2-txt3.get_width()//2, 240))
    WINDOW.blit(txt4, (WIDTH//2-txt4.get_width()//2, 280))
    pygame.display.flip()
    pygame.time.wait(3400)

def main():
    print_khezu()
    clock = pygame.time.Clock()
    player = Player()
    khezus = pygame.sprite.Group()
    global bullets
    bullets = pygame.sprite.Group()
    effects = pygame.sprite.Group()
    
    bg_x = 0
    bg2_x = WIDTH
    score = 0
    timer = 0

    for _ in range(2):
        khezus.add(KhezuMonster())

    running = True
    win = False
    while running:
        dt = clock.tick(FPS)
        timer += dt
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()

        player.update(keys)
        khezus.update()
        bullets.update()
        effects.update()
        
        hits = [k for k in khezus if pygame.sprite.spritecollideany(k, bullets)]
        if hits:
            for k in hits:
                k.respawn()
                bullets.remove(pygame.sprite.spritecollideany(k, bullets))
        
        player_hits = [k for k in khezus if player.rect.colliderect(k.rect)]
        if player_hits:
            SCHLING.play()
            effects.add(Effect(player.rect.center))
            player.lives -= 1
            for k in player_hits:
                k.respawn()
            if player.lives <= 0:
                gameover_screen("perdu", score//1000)
                running = False

        bg_x -= 1
        bg2_x -= 1
        if bg_x <= -WIDTH: bg_x = WIDTH
        if bg2_x <= -WIDTH: bg2_x = WIDTH

        blit_bg(BACKGROUND, bg_x)
        blit_bg(BACKGROUND2, bg2_x)
        khezus.draw(WINDOW)
        WINDOW.blit(player.image, player.rect)
        bullets.draw(WINDOW)
        draw_hearts(player.lives)
        effects.draw(WINDOW)
        txt = FONT.render(f"Survie : {score//1000} sec", 1, (230, 230, 230))
        WINDOW.blit(txt, (WIDTH-220, 10))
        
        if score//1000 >= 45:
            gameover_screen("gagné", score//1000)
            win = True
            running = False

        pygame.display.flip()
        score += dt

    pygame.quit()

main()