import pygame
import sys
import os
import random

pygame.init()
WIDTH, HEIGHT = 640, 480
FPS = 60

os.chdir(r"C:\Users\Malkai\Desktop\Streaming\Images")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khezu Street Dash")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 28)
font_big = pygame.font.SysFont("consolas", 48)

bg_img1 = pygame.image.load("background1.png").convert()
bg_img2 = pygame.image.load("background2.png").convert()
bg_imgs = [bg_img1, bg_img2]

player_img = pygame.image.load("KhezuL.png").convert_alpha()
goal_img = pygame.image.load("BLcheers.gif").convert_alpha()
enemy_img = pygame.image.load("ksekos.png").convert_alpha()
item_img = pygame.image.load("Pweto.png").convert_alpha()
effect_sheet = pygame.image.load("effetanim14.png").convert_alpha()
effect_frames = [effect_sheet.subsurface(pygame.Rect(i*64, 0, 64, 64)) for i in range(effect_sheet.get_width() // 64)]

bg_music = "cyberpunk-street.mp3"
item_sound = "schling2.mp3"
lose_sound = "Piano relaxant3.mp3"
win_sound = "The moment.mp3"

pygame.mixer.music.load(bg_music)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

item_fx = pygame.mixer.Sound(item_sound)
item_fx.set_volume(0.5)
win_fx = pygame.mixer.Sound(win_sound)
win_fx.set_volume(0.5)
lose_fx = pygame.mixer.Sound(lose_sound)
lose_fx.set_volume(0.5)

bg_scroll = 0

class Player:
    def __init__(self):
        self.img = pygame.transform.scale(player_img, (64, 64))
        self.x = 40
        self.y = HEIGHT//2
        self.rect = pygame.Rect(self.x, self.y, 48, 48)
        self.vel = 4
        self.move_y = 0
        self.lives = 3
        self.score = 0
        self.invuln = 0

    def move(self):
        keys = pygame.key.get_pressed()
        self.move_y = 0
        if keys[pygame.K_UP]:
            self.move_y = -self.vel
        if keys[pygame.K_DOWN]:
            self.move_y = self.vel
        self.y += self.move_y
        self.y = max(0, min(HEIGHT-64, self.y))
        self.rect.topleft = (self.x, self.y)
        if self.invuln > 0:
            self.invuln -= 1

    def draw(self, surf):
        if self.invuln % 10 < 5:
            surf.blit(self.img, (self.x, self.y))

class Enemy:
    def __init__(self):
        self.img = pygame.transform.scale(enemy_img, (48,48))
        self.x = WIDTH + random.randint(0,120)
        self.y = random.randint(20, HEIGHT-70)
        self.velx = random.randint(4, 8)
        self.rect = pygame.Rect(self.x, self.y, 38, 38)

    def move(self):
        self.x -= self.velx
        if self.x < -50:
            self.x = WIDTH + random.randint(0,150)
            self.y = random.randint(10, HEIGHT-58)
            self.velx = random.randint(4, 8)
        self.rect.topleft = (self.x, self.y)

    def draw(self, surf):
        surf.blit(self.img, (self.x, self.y))

class Item:
    def __init__(self):
        self.img = pygame.transform.scale(item_img, (32,32))
        self.x = WIDTH + random.randint(0, 400)
        self.y = random.randint(30, HEIGHT-40)
        self.rect = pygame.Rect(self.x, self.y, 28, 28)

    def move(self):
        self.x -= 5
        if self.x < -40:
            self.x = WIDTH + random.randint(100,300)
            self.y = random.randint(20, HEIGHT-40)
        self.rect.topleft = (self.x, self.y)

    def draw(self, surf):
        surf.blit(self.img, (self.x, self.y))

class Goal:
    def __init__(self):
        self.img = pygame.transform.scale(goal_img, (48, 48))
        self.x = WIDTH + 128
        self.y = HEIGHT // 2
        self.rect = pygame.Rect(self.x, self.y, 40, 40)
        self.shown = False

    def move(self):
        if self.shown:
            self.x -= 4
            self.rect.topleft = (self.x, self.y)

    def draw(self, surf):
        if self.shown:
            surf.blit(self.img, (self.x, self.y))

class Effect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.done = False

    def update(self):
        self.frame += 0.5
        if self.frame >= len(effect_frames):
            self.done = True

    def draw(self, surf):
        if not self.done:
            surf.blit(effect_frames[int(self.frame)], (self.x, self.y))

player = Player()
enemies = [Enemy() for _ in range(3)]
items = [Item() for _ in range(2)]
goal = Goal()
effects = []

game_over = False
game_win = False
goal_reached = False
scroll_speed = 3
score_target = 6
frame_switch = 0

def draw_bg():
    global bg_scroll, frame_switch
    bg_scroll = (bg_scroll + scroll_speed) % WIDTH
    cur_bg = bg_imgs[frame_switch // 50 % 2]
    screen.blit(cur_bg, (-bg_scroll,0))
    screen.blit(cur_bg, (WIDTH-bg_scroll,0))
    frame_switch += 1

def show_text(msg, y, big=False):
    surf = font_big.render(msg, True, (255,255,255)) if big else font.render(msg,True,(255,255,255))
    rect = surf.get_rect(center=(WIDTH//2, y))
    screen.blit(surf, rect)

def draw_stats():
    show_text(f"Score: {player.score}", 34)
    show_text(f"Lives: {player.lives}", 68)
    show_text("Khezu power!", HEIGHT-26)

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over or game_win:
            if e.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()
    draw_bg()
    if not game_over and not game_win:
        player.move()
        player.draw(screen)
        for enemy in enemies:
            enemy.move()
            enemy.draw(screen)
        for item in items:
            item.move()
            item.draw(screen)
        to_del = []
        for eff in effects:
            eff.update()
            eff.draw(screen)
            if eff.done: to_del.append(eff)
        for e in to_del: effects.remove(e)
        if player.score >= score_target and not goal.shown:
            goal.shown = True
            print("Khezu approves, you reached the target!")
        if goal.shown and not goal_reached:
            goal.move()
            goal.draw(screen)
        for item in items:
            if player.rect.colliderect(item.rect):
                effects.append(Effect(item.x-10,item.y-10))
                player.score += 1
                item_fx.play()
                item.x = WIDTH + random.randint(80,300)
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                if player.invuln == 0:
                    player.lives -= 1
                    effects.append(Effect(player.x-10,player.y-10))
                    player.invuln = 60
                    print("Khezu crie, attention au danger !")
                    if player.lives <= 0:
                        game_over = True
                        pygame.mixer.music.stop()
                        lose_fx.play()
        if player.lives > 0 and goal.shown and player.rect.colliderect(goal.rect) and not goal_reached:
            goal_reached = True
            game_win = True
            pygame.mixer.music.stop()
            win_fx.play()
        draw_stats()
    else:
        screen.fill((10,14,30))
        if game_over:
            show_text("GAME OVER", HEIGHT//2-42, True)
        else:
            show_text("VICTOIRE!", HEIGHT//2-42, True)
        show_text("Code par tchat", HEIGHT//2+10)
        show_text("Art par ansimuz, BDragon1727", HEIGHT//2+40)
        show_text("Appuie sur une touche pour quitter", HEIGHT-42)
        if game_over:
            show_text("Le monstre Khezu t'a vaincu...", HEIGHT//2+80)
        else:
            show_text("Khezu célèbre ta victoire!", HEIGHT//2+80)
        pygame.display.flip()
        continue
    pygame.display.flip()
    clock.tick(FPS)