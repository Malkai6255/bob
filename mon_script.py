import pygame
import sys
import os
import random
from pygame.locals import *

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
FPS = 60

WINDOW_WIDTH, WINDOW_HEIGHT = 960, 540
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Khezu Clicker")

img_path = "C:\\Users\\Malkai\\Desktop\\Streaming\\Images"
def load_img(name, alpha=False):
    path = os.path.join(img_path, name)
    if alpha:
        return pygame.image.load(path).convert_alpha()
    else:
        return pygame.image.load(path).convert()

def load_sound(name):
    s = pygame.mixer.Sound(os.path.join(img_path, name))
    s.set_volume(0.5)
    return s

def load_music(name):
    pygame.mixer.music.load(os.path.join(img_path, name))
    pygame.mixer.music.set_volume(0.5)

backgrounds = [
    load_img("background1.png"),
    load_img("background2.png"),
    load_img("cyberpunk-street.png")
]
bg_idx = 0

khezu_img = pygame.transform.scale(load_img("KhezuL.png", True), (256,192))
khezu_rect = khezu_img.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
btn_font = pygame.font.SysFont("consolas", 32, bold=True)
score_font = pygame.font.SysFont("consolas", 28, bold=True)
big_font = pygame.font.SysFont("consolas", 60, bold=True)
small_font = pygame.font.SysFont("consolas", 18)

click_sound = load_sound("schling.mp3")
buy_sound = load_sound("schling2.mp3")
win_sound = load_sound("Piano relaxant3.mp3")
lose_sound = load_sound("The moment.mp3")
auto_sound = load_sound("Piano relaxant2.mp3")
celebrate_gif = load_img("BLcheers.gif", True)

max_score = 6969696969696969
score = 0
khezu_per_click = 1
auto_khezu = 0
auto_khezu_timer = 0
auto_khezu_interval = 1000
auto_khezu_level = 0
auto_khezu_cost = 50
win = False
lose = False
show_credits = False
bg_anim_timer = 0
bg_anim_interval = 2200
fail_time_limit = 250 # seconds
start_ticks = pygame.time.get_ticks()
credits_screen = False
blink = False

# Simple effect animation for click
class EffectAnim(pygame.sprite.Sprite):
    def __init__(self, x, y, sheetname):
        super().__init__()
        self.sheet = load_img(sheetname, True)
        self.frames = []
        for i in range(self.sheet.get_width()//64):
            frame = self.sheet.subsurface((i*64,0,64,64))
            self.frames.append(frame)
        self.idx = 0
        self.image = self.frames[self.idx]
        self.rect = self.image.get_rect(center=(x,y))
        self.timer = 0
    def update(self):
        self.timer += 1
        if self.timer % 2 == 0: self.idx += 1
        if self.idx>=len(self.frames): self.kill()
        else: self.image = self.frames[self.idx]

effects = pygame.sprite.Group()

def draw_button(rect, text, enabled=True):
    color = (200,220,255) if enabled else (90,90,90)
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (80,110,170), rect, 3, border_radius=12)
    tx = btn_font.render(text, True, (30,20,30) if enabled else (120,120,120))
    tx_rect = tx.get_rect(center=rect.center)
    screen.blit(tx, tx_rect)

def format_score(sc):
    if sc >= 1e12: return f"{sc//10**12}T"
    elif sc >= 1e9: return f"{sc//10**9}G"
    elif sc>=1e6: return f"{sc//10**6}M"
    elif sc>=1e3: return f"{sc//10**3}k"
    else: return str(sc)

def animate_khezu(osc):
    pos = khezu_rect.copy()
    pos.centery += int(8*osc)
    screen.blit(khezu_img, pos)

def draw_ui():
    global blink
    t = (pygame.time.get_ticks()//420) % 2 == 0
    blink = t
    pygame.draw.rect(screen, (20,20,30), (10,10,WINDOW_WIDTH-20, 64), border_radius=16)
    s_surf = score_font.render(f"Khezu: {format_score(score)}", True, (255,240,240) if blink else (255,190,190))
    screen.blit(s_surf, (24,24))
    need = score/max_score
    pygame.draw.rect(screen, (45,0,0), (10,80,WINDOW_WIDTH-20,10), border_radius=4)
    pygame.draw.rect(screen, (250,100,220), (10,80,int((WINDOW_WIDTH-20)*need),10), border_radius=4)
    screen.blit(score_font.render(f"Goal: {max_score}", True, (220,220,220)), (WINDOW_WIDTH//2+180,24))
    s_auto = score_font.render(f"AutoKhezu: {auto_khezu_level} (+{auto_khezu}/sec)", True, (200,255,220))
    screen.blit(s_auto, (24,54))

def draw_shop():
    rect = pygame.Rect(WINDOW_WIDTH-330, WINDOW_HEIGHT-110, 320, 90)
    pygame.draw.rect(screen, (24,28,34), rect, border_radius=16)
    pygame.draw.rect(screen, (110,160,200), rect, 2, border_radius=16)
    tx = btn_font.render("SHOP", True, (148,255,224))
    screen.blit(tx, (rect.x+8, rect.y+7))
    btn = pygame.Rect(rect.x+18, rect.y+45, 184,38)
    draw_button(btn, f"+1 AutoKhezu ({auto_khezu_cost})", enabled=(score>=auto_khezu_cost))
    return btn

def draw_timer():
    elapsed = (pygame.time.get_ticks()-start_ticks)//1000
    left = max(0, fail_time_limit-elapsed)
    timer = score_font.render(f"Time left: {left}s", True, (248,210,180))
    screen.blit(timer, (WINDOW_WIDTH-210,10))
    return left

def show_win():
    screen.blit(backgrounds[2], (0,0))
    screen.blit(celebrate_gif, (WINDOW_WIDTH//2-150, WINDOW_HEIGHT//2-120))
    t1 = big_font.render("VICTOIRE!", True, (255,200,255))
    t2 = score_font.render("Khezu suprême est content", True, (225,170,200))
    screen.blit(t1, (WINDOW_WIDTH//2-t1.get_width()//2, 60))
    screen.blit(t2, (WINDOW_WIDTH//2-t2.get_width()//2, 160))
    cred = small_font.render("Code: tchat | Art: ansimuz, BDragon1727", True, (120,250,220))
    screen.blit(cred, (WINDOW_WIDTH//2-cred.get_width()//2, WINDOW_HEIGHT-70))
    t3 = score_font.render("Merci d'avoir élevé le Khezu.", True, (250,250,250))
    screen.blit(t3, (WINDOW_WIDTH//2-t3.get_width()//2, 260))
    t4 = score_font.render("Appuie sur Echap ou ferme la fenêtre.", True, (200,220,230))
    screen.blit(t4, (WINDOW_WIDTH//2-t4.get_width()//2, 310))

def show_lose():
    screen.fill((20,16,32))
    t1 = big_font.render("ECHEC", True, (255,80,100))
    t2 = score_font.render("Trop lent! Le Khezu s'est échappé.", True, (230,70,70))
    screen.blit(t1, (WINDOW_WIDTH//2-t1.get_width()//2, 90))
    screen.blit(t2, (WINDOW_WIDTH//2-t2.get_width()//2, WINDOW_HEIGHT//2-20))
    cred = small_font.render("Code: tchat | Art: ansimuz, BDragon1727", True, (220,120,220))
    screen.blit(cred, (WINDOW_WIDTH//2-cred.get_width()//2, WINDOW_HEIGHT-70))
    t3 = score_font.render("Appuie sur Echap ou ferme la fenêtre.", True, (210,200,220))
    screen.blit(t3, (WINDOW_WIDTH//2-t3.get_width()//2, WINDOW_HEIGHT//2+60))

def reset_game():
    global score, auto_khezu, auto_khezu_timer, auto_khezu_level, auto_khezu_cost, win, lose, show_credits, start_ticks
    score = 0
    auto_khezu = 0
    auto_khezu_timer = 0
    auto_khezu_level = 0
    auto_khezu_cost = 50
    win = False
    lose = False
    show_credits = False
    start_ticks = pygame.time.get_ticks()
    pygame.mixer.music.stop()

def spawn_effect(x, y):
    effects.add(EffectAnim(x, y, f"effetanim{random.choice([3,4,5,6,13,14,15,16,23,24,25,26]):02d}.png"))

print("KEZHU KEZHU KEZHU <3")
load_music("Piano relaxant.mp3")
pygame.mixer.music.play(-1)

bg_offset = 0.0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if win or lose:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        if not (win or lose):
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx,my = event.pos
                if khezu_rect.collidepoint(mx,my):
                    cval = khezu_per_click + auto_khezu_level//4
                    score += cval
                    click_sound.play()
                    spawn_effect(mx,my)
                shop_btn = draw_shop()
                if shop_btn.collidepoint(mx,my) and score>=auto_khezu_cost:
                    buy_sound.play()
                    score -= auto_khezu_cost
                    auto_khezu_level += 1
                    auto_khezu += 1
                    auto_khezu_cost = int(auto_khezu_cost*1.32+auto_khezu_level*7)
                    for i in range(2):
                        spawn_effect(shop_btn.centerx+random.randint(-10,10), shop_btn.centery+random.randint(-10,10))

    if not (win or lose):
        bg_anim_timer += clock.get_time()
        if bg_anim_timer > bg_anim_interval:
            bg_anim_timer = 0
            bg_idx = (bg_idx+1)%len(backgrounds)
        bg_offset += 0.05
        if bg_offset>=backgrounds[bg_idx].get_height():
            bg_offset = 0
        screen.blit(backgrounds[bg_idx], (0,0))
        draw_ui()
        animate_khezu(pygame.math.sin(pygame.time.get_ticks()/180))
        shop_btn = draw_shop()
        left = draw_timer()
        effects.update()
        effects.draw(screen)
        if auto_khezu_level>0:
            auto_khezu_timer += clock.get_time()
            if auto_khezu_timer >= 1000:
                auto_khezu_timer = 0
                score += auto_khezu
                auto_sound.play()
                spawn_effect(random.randint(khezu_rect.left, khezu_rect.right), khezu_rect.bottom+random.randint(-8,8))
        if score>=max_score:
            win = True
            pygame.mixer.music.fadeout(1500)
            win_sound.play()
        if left<=0 and not win:
            lose = True
            pygame.mixer.music.fadeout(1200)
            lose_sound.play()
    else:
        if win:
            show_win()
        elif lose:
            show_lose()
    pygame.display.flip()
    clock.tick(FPS)