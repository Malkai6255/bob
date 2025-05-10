import pygame
import sys
import random
import os

pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 960, 720
FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formes et Oeuvres - Khezu Edition")
CLOCK = pygame.time.Clock()
BASE_PATH = r"C:\Users\Malkai\Desktop\Streaming\Images"

def load_img(name, alpha=True):
    surf = pygame.image.load(os.path.join(BASE_PATH, name))
    return surf.convert_alpha() if alpha else surf.convert()

def play_music(name, vol=0.5):
    pygame.mixer.music.load(os.path.join(BASE_PATH, name))
    pygame.mixer.music.set_volume(vol)
    pygame.mixer.music.play(-1)

def play_sound(name):
    s = pygame.mixer.Sound(os.path.join(BASE_PATH, name))
    s.set_volume(0.5)
    s.play()

def draw_text(surface, text, size, x, y, color=(255,255,255), center=True, fontname=None):
    font = pygame.font.Font(fontname, size)
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(txt, rect)

def get_random_color():
    return random.choice([(255, 0, 120), (60, 255, 220), (255, 255, 100), 
                         (180, 40, 255), (255, 130, 40), (60, 142, 255)])

def sprite_sheet_frames(sheet, frame_w, frame_h):
    sheet_img = load_img(sheet)
    sheet_rect = sheet_img.get_rect()
    frames = []
    for y in range(0, sheet_rect.height, frame_h):
        for x in range(0, sheet_rect.width, frame_w):
            frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            frame.blit(sheet_img, (0, 0), pygame.Rect(x, y, frame_w, frame_h))
            frames.append(frame)
    return frames

class EffectAnim(pygame.sprite.Sprite):
    def __init__(self, sheet, pos):
        super().__init__()
        self.frames = sprite_sheet_frames(sheet, 64, 64)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)
        self.index = 0
        self.timer = 0
    
    def update(self):
        self.timer += 1
        if self.timer % 4 == 0:
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]
                self.rect = self.image.get_rect(center=self.rect.center)

class KhezuSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.img = load_img("KhezuL.png")
        self.image = pygame.transform.scale(self.img, (128, 128))
        self.rect = self.image.get_rect(center=(WIDTH-90, HEIGHT//2))
        self.dir = 1

    def update(self):
        self.rect.y += self.dir * random.randint(0, 2)
        if self.rect.top < 20 or self.rect.bottom > HEIGHT-20:
            self.dir *= -1

class Shape(pygame.sprite.Sprite):
    def __init__(self, shape, pos, color, size):
        super().__init__()
        self.shape = shape
        self.color = color
        self.pos = pos
        self.size = size
        self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        if shape == "circle":
            pygame.draw.circle(self.image, color, (size, size), size)
        elif shape == "rect":
            pygame.draw.rect(self.image, color, (0, 0, size*2, size*2))
        elif shape == "triangle":
            pygame.draw.polygon(self.image, color, 
                [(size, 0), (0, size*2), (size*2, size*2)])
        elif shape == "kezu":
            sprite = load_img("KhezuL.png")
            sprite = pygame.transform.scale(sprite, (size*2, size*2))
            self.image.blit(sprite, (0, 0))
        self.rect = self.image.get_rect(center=pos)

class ArtTarget:
    def __init__(self):
        self.shapes = []
        for _ in range(8):
            t = random.choice(["circle", "rect", "triangle"])
            pos = (random.randint(120, WIDTH-220), random.randint(120, HEIGHT-220))
            color = get_random_color()
            size = random.randint(20, 60)
            self.shapes.append((t, pos, color, size))
    
    def draw(self, surface):
        for t, pos, col, sz in self.shapes:
            surf = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
            if t == "circle":
                pygame.draw.circle(surf, col, (sz, sz), sz)
            elif t == "rect":
                pygame.draw.rect(surf, col, (0, 0, sz*2, sz*2))
            elif t == "triangle":
                pygame.draw.polygon(surf, col, [(sz, 0), (0, sz*2), (sz*2, sz*2)])
            surface.blit(surf, (pos[0]-sz, pos[1]-sz))
        
def compare_art(player, target):
    hits = 0
    for t in target.shapes:
        for s in player:
            if (s.shape == t[0] and 
                abs(s.pos[0]-t[1][0]) < t[3] and
                abs(s.pos[1]-t[1][1]) < t[3] and
                s.color == t[2]):
                hits += 1
                break
    return hits

def start_screen():
    bg = load_img("cyberpunk-street.png")
    play_music("Piano relaxant3.mp3")
    timer = 0
    art = ArtTarget()
    blink = True
    while True:
        WIN.blit(bg, (0,0))
        art.draw(WIN)
        draw_text(WIN, "Formes & Oeuvres", 62, WIDTH//2, 110, (255,240,200))
        if blink:
            draw_text(WIN, "Appuyez sur ESPACE pour commencer", 26, WIDTH//2, HEIGHT-120, (255,120,220))
        draw_text(WIN, "Objectif : reproduisez l'oeuvre!", 32, WIDTH//2, HEIGHT-190, (210,255,220))
        draw_text(WIN, "Art par ansimuz, BDragon1727", 22, WIDTH//2, HEIGHT-40, (120,170,255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                play_sound("schling2.mp3")
                return art
        timer += 1
        if timer % 30 == 0: blink = not blink
        pygame.display.flip()
        CLOCK.tick(FPS)

def end_screen(win, score, maxscore):
    bg = load_img("background2.png")
    play_music("The moment.mp3")
    timer = 0
    blink = True
    while True:
        WIN.blit(bg, (0,0))
        if win:
            draw_text(WIN, "Bravo! Vous avez réussi!", 54, WIDTH//2, 110, (60,255,120))
            draw_text(WIN, "Khezu t'aime! ♥", 32, WIDTH//2, 160, (255,200,255))
        else:
            draw_text(WIN, "Raté! Khezu est déçu...", 54, WIDTH//2, 110, (255,80,80))
            draw_text(WIN, "Essayez encore!", 28, WIDTH//2, 160, (255,255,255))
        draw_text(WIN, f"Score: {score}/{maxscore}", 30, WIDTH//2, 210)
        draw_text(WIN, "code: tchat  |  art: ansimuz, BDragon1727", 20, WIDTH//2, HEIGHT-40, (170,120,255))
        if blink:
            draw_text(WIN, "ESPACE = recommencer   |   ECHAP = quitter", 26, WIDTH//2, HEIGHT-80, (120,200,255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return True
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
        timer += 1
        if timer % 30 == 0: blink = not blink
        pygame.display.flip()
        CLOCK.tick(FPS)

def main_game(target):
    print("Khezu > EVERY GAME IS BETTER WITH KHEZU")
    bg = load_img("background1.png")
    play_music("Piano relaxant.mp3")
    player_shapes = pygame.sprite.Group()
    effectanims = pygame.sprite.Group()
    khezu = KhezuSprite()
    clock = pygame.time.Clock()
    timer = 60 * 45  # 45 secondes
    selected_shape = "circle"
    current_color = get_random_color()
    current_size = 40
    running = True
    lastpos = None

    while running:
        clock.tick(FPS)
        timer -= 1
        WIN.blit(bg, (0,0))
        target.draw(WIN)

        for s in player_shapes: WIN.blit(s.image, s.rect)
        effectanims.update()
        effectanims.draw(WIN)
        khezu.update()
        WIN.blit(khezu.image, khezu.rect)

        draw_text(WIN, "Sélectionnez forme: [1]○ [2]□ [3]△ [4]Khezu", 26, 180, 40, (240,255,220), center=False)
        draw_text(WIN, "Couleur: C-Change | +/- Taille | Z-Undo | F-Feu Effet | SPACE-Finir", 24, 18, HEIGHT-40, (220,250,255),center=False)
        draw_text(WIN, "Temps: "+str(timer//FPS).rjust(2,"0"), 32, WIDTH-120, 30, (234,210,255))
        draw_text(WIN, "OBJECTIF: reproduire l'oeuvre à gauche!", 24, WIDTH-380, HEIGHT-60, (240,220,255))
        pygame.draw.rect(WIN, current_color, (12,12,48,48))
        pygame.draw.rect(WIN, (50,40,44), (10,10,52,52),2)
        draw_text(WIN, str(current_size), 22, 36, 70, (current_color))
        shape_icon = None
        if selected_shape == "circle":
            shape_icon = pygame.Surface((38,38), pygame.SRCALPHA); pygame.draw.circle(shape_icon, current_color, (19,19), 19)
        elif selected_shape == "rect":
            shape_icon = pygame.Surface((38,38), pygame.SRCALPHA); pygame.draw.rect(shape_icon, current_color, (0,0,38,38))
        elif selected_shape == "triangle":
            shape_icon = pygame.Surface((38,38), pygame.SRCALPHA);
            pygame.draw.polygon(shape_icon, current_color, [(19,0),(0,38),(38,38)])
        elif selected_shape == "kezu":
            shape_icon = load_img("KhezuL.png")
            shape_icon = pygame.transform.scale(shape_icon, (38,38))
        if shape_icon: WIN.blit(shape_icon, (64,18))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: selected_shape = "circle"
                if event.key == pygame.K_2: selected_shape = "rect"
                if event.key == pygame.K_3: selected_shape = "triangle"
                if event.key == pygame.K_4: selected_shape = "kezu"
                if event.key == pygame.K_c: current_color = get_random_color()
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    current_size = min(64, current_size+4)
                if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    current_size = max(16, current_size-4)
                if event.key == pygame.K_z and len(player_shapes)>0:
                    player_shapes.remove(player_shapes.sprites()[-1])
                    play_sound("schling2.mp3")
                if event.key == pygame.K_f:
                    fr = random.choice(['effetanim03.png', 'effetanim05.png', 'effetanim24.png', 'effetanim25.png'])
                    p = (random.randint(90, WIDTH-90), random.randint(100, HEIGHT-100))
                    effectanims.add(EffectAnim(fr, p))
                    play_sound("schling.mp3")
                if event.key == pygame.K_SPACE:
                    play_sound("schling2.mp3")
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if mx > 0 and mx < WIDTH:
                    player_shapes.add(Shape(selected_shape, (mx,my), current_color, current_size))
                    play_sound("schling.mp3")
            if event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                mx, my = pygame.mouse.get_pos()
                if lastpos is not None and abs(mx-lastpos[0])+abs(my-lastpos[1]) > current_size//2:
                    player_shapes.add(Shape(selected_shape, (mx,my), current_color, current_size))
                    play_sound("schling.mp3")
                lastpos = (mx, my)
        if timer <= 0:
            running = False
        pygame.display.flip()

    player = list(player_shapes)
    maxscore = len(target.shapes)
    score = compare_art(player, target)
    return (score, maxscore)

def main():
    while True:
        target = start_screen()
        score, maxscore = main_game(target)
        win = (score >= maxscore * 0.75)
        again = end_screen(win, score, maxscore)
        if not again:
            break

main()