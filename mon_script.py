import pygame
import random
import threading
import socket
import time
import os

WIDTH, HEIGHT = 900, 540
FPS = 60
BG_COLOR = (24, 17, 28)
IMAGE_DIR = r"C:\Users\Malkai\Desktop\Streaming\Images"
SPRITE_SIZE = 64

IRC_SERVER = "irc.chat.twitch.tv"
IRC_PORT = 6667
NICK = "justinfan1337"
OAUTH = "oauth:1337"  # Pseudo guest pour lecture
CHANNEL = "#votretwitch" # À changer pour votre channel

pygame.init()
pygame.font.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Twitch Wheel of Fate")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)
bigfont = pygame.font.SysFont("Arial Black", 52)
tinyfont = pygame.font.SysFont("Arial", 22, bold=True)

BACKGROUND = pygame.image.load(os.path.join(IMAGE_DIR, "cyberpunk-street.png")).convert()
BACKGROUND = pygame.transform.smoothscale(BACKGROUND, (WIDTH, HEIGHT))
WHEEL = pygame.image.load(os.path.join(IMAGE_DIR, "BLcheers.gif"))
WHEEL = pygame.transform.smoothscale(WHEEL, (220, 220))
KHEZU = pygame.image.load(os.path.join(IMAGE_DIR, "KhezuL.png"))
KHEZU = pygame.transform.smoothscale(KHEZU, (130, 130))

ANIM_FRAMESHEET = pygame.image.load(os.path.join(IMAGE_DIR, "effetanim15.png"))

if os.path.exists(os.path.join(IMAGE_DIR, "schling.mp3")):
    schling_fx = pygame.mixer.Sound(os.path.join(IMAGE_DIR, "schling.mp3"))
    schling_fx.set_volume(0.5)
else:
    schling_fx = None
if os.path.exists(os.path.join(IMAGE_DIR, "Piano relaxant.mp3")):
    pygame.mixer.music.load(os.path.join(IMAGE_DIR, "Piano relaxant.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
else:
    pygame.mixer.music.stop()

def get_sheet_anim(sheet):
    frames = []
    w, h = sheet.get_size()
    for y in range(0, h, SPRITE_SIZE):
        for x in range(0, w, SPRITE_SIZE):
            frames.append(sheet.subsurface((x, y, SPRITE_SIZE, SPRITE_SIZE)))
    return frames

ANIM_FRAMES = get_sheet_anim(ANIM_FRAMESHEET)

def irc_thread(pseudos):
    s = socket.socket()
    try:
        s.connect((IRC_SERVER, IRC_PORT))
        s.send(f"PASS {OAUTH}\r\n".encode('utf-8'))
        s.send(f"NICK {NICK}\r\n".encode('utf-8'))
        s.send(f"JOIN {CHANNEL}\r\n".encode('utf-8'))
        print("Khezu IRC love!")
        while True:
            data = s.recv(1024).decode('utf-8')
            lines = data.split('\r\n')
            for line in lines:
                if "PING" in line:
                    s.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
                if "PRIVMSG" in line:
                    pseudo = line.split('!', 1)[0][1:]
                    if pseudo and pseudo not in pseudos:
                        pseudos.append(pseudo)
            time.sleep(0.05)
    except Exception as e:
        print("Khezu sad: no IRC", e)
    finally:
        s.close()

def draw_ban_overlay(target):
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((70,0,0,180))
    screen.blit(s, (0,0))
    txt = bigfont.render("BANNI 2m!", True, (200,30,30))
    screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT//2-txt.get_height()//2-20))
    screen.blit(KHEZU, (WIDTH//2-60, HEIGHT//2+60))
    pseudo = font.render(target, True, (255,200,200))
    screen.blit(pseudo, (WIDTH//2-pseudo.get_width()//2, HEIGHT//2+40))

def draw_modo_overlay(target):
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((60,80,20,170))
    screen.blit(s, (0,0))
    txt = bigfont.render("PROMU MODO!", True, (120,255,120))
    screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT//2-txt.get_height()//2-20))
    pseudo = font.render(target, True, (120,255,120))
    screen.blit(pseudo, (WIDTH//2-pseudo.get_width()//2, HEIGHT//2+40))

def draw_nothing_overlay(target):
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((90,90,120,120))
    screen.blit(s, (0,0))
    txt = bigfont.render("...Rien ne se passe...", True, (200,200,250))
    screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT//2-txt.get_height()//2-20))
    pseudo = font.render(target, True, (200,200,250))
    screen.blit(pseudo, (WIDTH//2-pseudo.get_width()//2, HEIGHT//2+40))

def draw_credits(win):
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((10,10,18,220))
    screen.blit(s, (0,0))
    if win:
        msg = "VICTOIRE!"
        col = (190,255,200)
    else:
        msg = "VOUS AVEZ PERDU!"
        col = (230,140,120)
    txt = bigfont.render(msg, True, col)
    screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT//2-140))
    y = HEIGHT//2-10
    credits = [
        "Code par tchat",
        "Art par ansimuz, BDragon1727",
        "Merci d'avoir joué.",
        "Appuyez sur une touche pour quitter."
    ]
    for c in credits:
        ct = font.render(c, True, (220,220,220))
        screen.blit(ct, (WIDTH//2-ct.get_width()//2, y))
        y += 50

def draw_anim(anim_frames, timer, pos):
    idx = int((timer*FPS//2)%len(anim_frames))
    frame = anim_frames[idx]
    screen.blit(frame, pos)

def pseudo_display(pseudo, y, col=(220,220,250)):
    surf = font.render(pseudo, True, col)
    x = WIDTH//2 - surf.get_width()//2
    screen.blit(surf, (x, y))

def wheel_of_fate():
    state = "idle"
    timer = 0
    wheel_angle = 0
    pseudos = []
    picked = []
    threading.Thread(target=irc_thread, args=(pseudos,), daemon=True).start()
    wait_for = 3
    actions = []
    score = 0
    rounds = 5
    round_left = rounds
    outcome = None
    pseudo = ""
    ban_list = {}
    modus = set()
    anim_timer = 0
    can_quit = False
    fade = 0

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); exit()
            if can_quit and ev.type == pygame.KEYDOWN:
                return

        screen.blit(BACKGROUND, (0,0))

        if fade>0:
            s = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0,fade))
            screen.blit(s,(0,0))

        if state=="idle":
            txt = font.render("Appuyez sur ESPACE pour tirer un destin!", True, (200,255,200))
            screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT-80))
            if len(pseudos)>0:
                sample = [p for p in pseudos if p not in picked and p not in ban_list]
                y = 90
                random.shuffle(sample)
                for s in sample[:7]:
                    pseudo_display(s, y)
                    y += 38
            else:
                txt = font.render("(Connexion au chat Twitch...)", True, (180,180,180))
                screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT//2))
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                available = [p for p in pseudos if p not in picked and p not in ban_list]
                if available:
                    pseudo = random.choice(available)
                    state = "spinning"
                    timer = 0
                    schling_fx and schling_fx.play()
                else:
                    round_left = 0
                    outcome = False
                    state = "end"
                    fade=240
        elif state=="spinning":
            picked.append(pseudo)
            wheel_angle += 24
            timer += 1/FPS
            screen.blit(WHEEL, (WIDTH//2-110, HEIGHT//2-110))
            draw_anim(ANIM_FRAMES, timer, (80, HEIGHT//2-64))
            pseudo_display(pseudo, HEIGHT//2+120, (255,230,130))
            if timer>=1.8:
                res = random.choices(["nothing","ban","modo"], [0.34,0.33,0.33])[0]
                if res=="ban":
                    ban_list[pseudo]=time.time()+120
                    actions.append((pseudo,"ban"))
                    score+=1
                    state="ban"
                    schling_fx and schling_fx.play()
                elif res=="modo":
                    modus.add(pseudo)
                    actions.append((pseudo,"modo"))
                    state="modo"
                    schling_fx and schling_fx.play()
                else:
                    actions.append((pseudo,"rien"))
                    state="nothing"
                timer = 0
        elif state=="ban":
            draw_ban_overlay(pseudo)
            timer += 1/FPS
            if timer>2.7:
                round_left -= 1
                state = "idle" if round_left>0 else "end"
                outcome = True if score>=3 else False
                fade=0 if state=="idle" else 240
        elif state=="modo":
            draw_modo_overlay(pseudo)
            timer += 1/FPS
            if timer>2.3:
                round_left -= 1
                state = "idle" if round_left>0 else "end"
                outcome = True if score>=3 else False
                fade=0 if state=="idle" else 240
        elif state=="nothing":
            draw_nothing_overlay(pseudo)
            timer += 1/FPS
            if timer>2.1:
                round_left -= 1
                state = "idle" if round_left>0 else "end"
                outcome = True if score>=3 else False
                fade=0 if state=="idle" else 240
        elif state=="end":
            draw_credits(outcome)
            can_quit = True

        for p in list(ban_list.keys()):
            if time.time()>ban_list[p]:
                del ban_list[p]

        ct = tinyfont.render(f"Round: {rounds-round_left+1}/{rounds}", True, (150,220,240))
        screen.blit(ct, (24, 510))
        ktxt = tinyfont.render("Khezu <3", True, (180,120,220))
        screen.blit(ktxt, (WIDTH-ktxt.get_width()-15, 6))
        anim_timer += 1/FPS

        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
    wheel_of_fate()