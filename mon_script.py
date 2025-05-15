import pygame
import sys
import os
import random

pygame.init()
WIDTH, HEIGHT = 640, 480
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10

os.chdir(r"C:\Users\Malkai\Desktop\Streaming\Images")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khezu Platformer")
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
        self.vel_y = 0
        self.on_ground = False
        self.lives = 3
        self.score = 0
        self.invuln = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self.y >= HEIGHT - 64:
            self.y = HEIGHT - 64
            self.on_ground = True
            self.vel_y = 0
        else:
            self.on_ground = False

        self.rect.topleft = (self.x, self.y)
        if self.invuln > 0:
            self.invuln -= 1

    def draw(self, surf):
        if self.invuln % 10 < 5:
            surf.blit(self.img, (self.x, self.y))

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surf):
        pygame.draw.rect(surf, (120, 198, 255), self.rect)

    def check_collision(self, player):
        if player.rect.colliderect(self.rect):
            if player.vel_y > 0:
                player.y = self.rect.top - player.rect.height
                player.vel_y = 0
                player.on_ground = True

class Game:
    def __init__(self):
        self.player = Player()
        self.platforms = self.create_platforms()
        self.enemies = [Enemy() for _ in range(3)]
        self.items = [Item() for _ in range(2)]
        self.goal = Goal()
        self.effects = []
        self.game_over = False
        self.game_win = False
        self.goal_reached = False
        self.scroll_speed = 3
        self.score_target = 6
        self.frame_switch = 0

    def create_platforms(self):
        return [
            Platform(100, HEIGHT - 100, 100, 20),
            Platform(250, HEIGHT - 150, 150, 20),
            Platform(450, HEIGHT - 200, 100, 20)
        ]

    def draw_bg(self):
        bg_scroll = (bg_scroll + self.scroll_speed) % WIDTH
        cur_bg = bg_imgs[self.frame_switch // 50 % 2]
        screen.blit(cur_bg, (-bg_scroll,0))
        screen.blit(cur_bg, (WIDTH-bg_scroll,0))
        self.frame_switch += 1

    def show_text(self, msg, y, big=False):
        surf = font_big.render(msg, True, (255,255,255)) if big else font.render(msg,True,(255,255,255))
        rect = surf.get_rect(center=(WIDTH//2, y))
        screen.blit(surf, rect)

    def draw_stats(self):
        self.show_text(f"Score: {self.player.score}", 34)
        self.show_text(f"Lives: {self.player.lives}", 68)
        self.show_text("Khezu power!", HEIGHT-26)

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    # NENON PAS BIEN : sys.exit()
                if self.game_over or self.game_win:
                    if e.type == pygame.KEYDOWN:
                        pygame.quit()
                        # NENON PAS BIEN : sys.exit()
            self.draw_bg()
            if not self.game_over and not self.game_win:
                self.player.move()
                self.player.draw(screen)
                for platform in self.platforms:
                    platform.draw(screen)
                    platform.check_collision(self.player)
                for enemy in self.enemies:
                    enemy.move()
                    enemy.draw(screen)
                for item in self.items:
                    item.move()
                    item.draw(screen)
                if self.player.score >= self.score_target and not self.goal.shown:
                    self.goal.shown = True
                    print("Khezu approves, you reached the target!")
                if self.goal.shown and not self.goal_reached:
                    self.goal.move()
                    self.goal.draw(screen)
                self.draw_stats()
            else:
                screen.fill((10,14,30))
                if self.game_over:
                    self.show_text("GAME OVER", HEIGHT//2-42, True)
                else:
                    self.show_text("VICTOIRE!", HEIGHT//2-42, True)
                self.show_text("Code par tchat", HEIGHT//2+10)
                self.show_text("Art par ansimuz, BDragon1727", HEIGHT//2+40)
                self.show_text("Appuie sur une touche pour quitter", HEIGHT-42)
                if self.game_over:
                    self.show_text("Le monstre Khezu t'a vaincu...", HEIGHT//2+80)
                else:
                    self.show_text("Khezu célèbre ta victoire!", HEIGHT//2+80)
                pygame.display.flip()
                continue
            pygame.display.flip()
            clock.tick(FPS)

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

game = Game()
game.run()