import pygame
import random
import sys
import os

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
WIDTH, HEIGHT = 800, 600
FPS = 60
MAP_TILE = 64
PLAYER_SPEED = 4
font = pygame.font.SysFont('consolas', 32)
smallfont = pygame.font.SysFont('consolas', 24)
clock = pygame.time.Clock()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khezu Quest: The Lost Colère")
ASSET = r"C:\Users\Malkai\Desktop\Streaming\Images"

def load_img(fn, alpha=True):
    img = pygame.image.load(os.path.join(ASSET, fn))
    return img.convert_alpha() if alpha else img.convert()

def load_music(name):
    pygame.mixer.music.load(os.path.join(ASSET, name))

def play_sound(name):
    pygame.mixer.Sound(os.path.join(ASSET, name)).play()

def draw_text(surface, text, pos, color=(255,255,255), fnt=font, bg=None):
    r = fnt.render(text, True, color, bg)
    surface.blit(r, pos)

def dialog_box(surface, lines, y=HEIGHT-170):
    pygame.draw.rect(surface, (20,20,40), (30, y, WIDTH-60, 140))
    pygame.draw.rect(surface, (240,240,255), (32, y+2, WIDTH-64, 136), 2)
    for i,line in enumerate(lines):
        draw_text(surface, line, (50, y+15+i*34), (250,250,250), smallfont)

class Map:
    def __init__(self):
        self.bg = load_img("background1.png", alpha=False)
        self.w, self.h = 10, 7
        self.tiles = [[0]*self.w for _ in range(self.h)]
        self.npcs = [
            {"pos":(3,2), "img":load_img("Pweto.png"), "dialog":
                [ "Pwetooo ! C'est dangereux par ici.", "Prends cette BLcheers et bonne chance!" ]},
            {"pos":(7,5), "img":load_img("tigre desssin.png"), "dialog":
                [ "Le colere a volé mon schling!", "Bats Khezu pour sauver le monde!"]},
        ]
        self.khezu_pos = (8,2)
        self.goal = (9,6)

    def draw(self, surface, px, py):
        for y in range(self.h):
            for x in range(self.w):
                sx, sy = x*MAP_TILE, y*MAP_TILE
                surface.blit(self.bg, (sx,sy), area=pygame.Rect(sx%WIDTH, sy%HEIGHT, MAP_TILE, MAP_TILE))
        for npc in self.npcs:
            x,y = npc["pos"]
            surface.blit(pygame.transform.scale(npc["img"], (MAP_TILE,MAP_TILE)), (x*MAP_TILE,y*MAP_TILE))
        kx,ky = self.khezu_pos
        surface.blit(pygame.transform.scale(load_img("KhezuL.png"), (MAP_TILE,MAP_TILE)), (kx*MAP_TILE,ky*MAP_TILE))
        gx,gy = self.goal
        surface.blit(load_img("colere.png"), (gx*MAP_TILE,gy*MAP_TILE))

    def npc_at(self, x,y):
        for npc in self.npcs:
            if (x,y)==npc["pos"]:
                return npc
        return None

    def is_khezu(self, x,y):
        return (x,y)==self.khezu_pos
    def is_goal(self,x,y):
        return (x,y)==self.goal

class Player:
    def __init__(self):
        self.x, self.y = 1, 1
        self.hp = 26
        self.maxhp = 26
        self.mana = 10
        self.img = pygame.transform.scale(load_img("toonlink-link.gif"), (MAP_TILE,MAP_TILE))
        self.inv = {"BLcheers":1}
        self.wins = 0

    def move(self,dx,dy,mapobj):
        tx,ty = self.x+dx, self.y+dy
        if 0<=tx<mapobj.w and 0<=ty<mapobj.h:
            self.x, self.y = tx, ty

def show_intro():
    running=True
    timer=0
    while running:
        WIN.fill((4, 6, 22))
        draw_text(WIN, "Khezu Quest: The Lost Colère", (110, 90),(240,30,30))
        draw_text(WIN, "(appuyez sur Espace pour commencer)", (160, 320), (190,230,255), smallfont)
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE:
                running=False
        clock.tick(FPS)

def random_event():
    return random.random() < 0.18

def battle(player, enemy, bg_img):
    battlebg = pygame.transform.scale(load_img(bg_img),(WIDTH,HEIGHT))
    eff_imgs = [pygame.image.load(os.path.join(ASSET, f"effetanim0{r}.png")) 
                for r in [3,4,5,6,13,14,15,16,23,24,25,26]]
    turn = "player"
    eff_timer = 0
    eff_img = None
    run_cooldown = 0
    msg = []
    while player.hp > 0 and enemy["hp"] > 0:
        WIN.blit(battlebg,(0,0))
        pygame.draw.rect(WIN,(8,8,60),(20,450,760,120))
        draw_text(WIN, f"{enemy['name']}  HP:{enemy['hp']}", (480,100), (255,90,90))
        WIN.blit(pygame.transform.scale(enemy['img'], (140,160)), (520,200))
        draw_text(WIN, f"Toi  HP:{player.hp}/{player.maxhp}", (50,100), (150,250,110))
        WIN.blit(player.img, (90,220))
        if eff_img:
            ix = (pygame.time.get_ticks()//80)%8; iy = (pygame.time.get_ticks()//320)%2
            WIN.blit(eff_img.subsurface(ix*64,iy*64,64,64), (450,180))
            eff_timer -= 1
            if eff_timer<=0: eff_img = None
        if msg:
            dialog_box(WIN, msg[-2:] if len(msg)>2 else msg, 470)
        else:
            draw_text(WIN, "[A]ttaquer   [B]Lcheers    [F]uir", (50, 500), (250,240,220), smallfont)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and not msg and run_cooldown<=0:
                if turn=="player":
                    if event.key==pygame.K_a:
                        dmg=random.randint(4,10)
                        play_sound("schling2.mp3")
                        enemy['hp']-=dmg
                        eff_img = pygame.transform.scale(eff_imgs[random.randint(0,11)], (512,128))
                        eff_timer=8
                        msg.append(f"Tu frappes {enemy['name']} pour {dmg}!")
                        turn="enemy"
                    elif event.key==pygame.K_b and player.inv.get("BLcheers",0)>0:
                        heal=random.randint(8,15)
                        play_sound("schling.mp3")
                        player.hp=min(player.maxhp, player.hp+heal)
                        player.inv["BLcheers"]-=1
                        msg.append("BLcheers! Santé+%d"%heal)
                        turn="enemy"
                    elif event.key==pygame.K_f:
                        if random.random()<.68:
                            msg.append("Tu t'échappes !")
                            pygame.time.wait(600)
                            return "run"
                        else:
                            msg.append("Pas de bol : tu restes coincé!")
                            turn = "enemy"
            elif event.type==pygame.KEYDOWN and msg:
                msg=[]
        if turn=="enemy" and not msg and run_cooldown<=0:
            pygame.time.wait(450)
            atk = random.choice(["charge", "cris", "lumin"])
            if atk=="charge":
                play_sound("schling2.mp3")
                dmg=random.randint(3,10)
                player.hp-=dmg
                msg.append(f"{enemy['name']} charge! -{dmg} HP")
            elif atk=="cris":
                play_sound("schling.mp3")
                dmg=random.randint(1,8)
                player.hp-=dmg
                msg.append(f"{enemy['name']} crie! -{dmg} HP")
            elif atk=="lumin":
                dmg=max(1,player.hp//6)
                player.hp-=dmg
                msg.append(f"{enemy['name']} s'illumine! -{dmg} HP")
            turn="player"
        clock.tick(FPS)
        run_cooldown = max(run_cooldown-1, 0)
    return "win" if player.hp>0 else "lose"

def npc_dialog(npc):
    running = True
    lines = npc["dialog"].copy()
    idx = 0
    while running:
        WIN.fill((8,8,60))
        WIN.blit(pygame.transform.scale(npc["img"], (200,200)), (WIDTH//2-100, 60))
        dialog_box(WIN, [ lines[idx] ])
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                idx+=1
                if idx>=len(lines): running=False
        clock.tick(FPS)

def victory_screen(win):
    WIN.fill((0,12,32))
    draw_text(WIN, "VICTOIRE!" if win else "GAME OVER", (290,120), (210,190,250) if win else (255,60,70))
    draw_text(WIN, "Merci d'avoir joué à Khezu Quest!", (130,220), (250,250,240), smallfont)
    draw_text(WIN, "Objectif: battre Khezu, récupérer le Colère.", (90,270),(230,255,170), smallfont)
    draw_text(WIN, "Crédits:", (340,340), (240,240,255), smallfont)
    draw_text(WIN, "code par tchat, art par ansimuz, BDragon1727", (180, 370), (210,240,255), smallfont)
    draw_text(WIN, "Appuie sur ESC pour quitter.", (250,470), (180,220,240), smallfont)
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN and e.key==pygame.K_ESCAPE: sys.exit()
        clock.tick(30)

def khezu_encounter_bg():
    return "background2.png"

def random_enemy():
    if random.random()<0.5:
        return {"name":"Pweto sauvage","hp":18,"img":load_img("Pweto.png")}
    else:
        return {"name":"Ksekos","hp":20,"img":load_img("ksekos.png")}

def khezu_boss():
    return {"name":"KHEZU","hp":37,"img":load_img("KhezuL.png")}

def main():
    show_intro()
    load_music("cyberpunk-street.mp3")
    pygame.mixer.music.play(-1)
    print("Khezu is Love, Khezu is Life.")
    world = Map()
    player = Player()
    encounter_cool = 40
    finished = False
    while not finished:
        WIN.fill((12,12,16))
        world.draw(WIN, player.x, player.y)
        WIN.blit(player.img, (player.x*MAP_TILE,player.y*MAP_TILE))
        draw_text(WIN, f"HP:{player.hp}/{player.maxhp}  BLcheers:{player.inv.get('BLcheers',0)}", (16,8), (255,255,240), smallfont)
        draw_text(WIN, "Obj: Colère, battrez Khezu! [Déplacez:ZQSD]", (220, 8), (210,220,255), smallfont)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.KEYDOWN:
                dx,dy = 0,0
                if event.key==pygame.K_z: dy=-1
                if event.key==pygame.K_s: dy=1
                if event.key==pygame.K_q: dx=-1
                if event.key==pygame.K_d: dx=1
                if dx or dy:
                    player.move(dx, dy, world)
                    encounter_cool = max(12,encounter_cool-1)
                    if world.is_goal(player.x,player.y):
                        victory_screen(True)
                    elif world.is_khezu(player.x,player.y):
                        res = battle(player, khezu_boss(), khezu_encounter_bg())
                        if res=="win":
                            player.wins+=1
                            draw_text(WIN, "Tu récupères le Colère!", (100, 320), (250,250,100), font)
                            pygame.display.flip()
                            pygame.time.wait(900)
                            victory_screen(True)
                        else:
                            victory_screen(False)
                    elif world.npc_at(player.x,player.y):
                        npc_dialog(world.npc_at(player.x,player.y))
                        if player.x==3 and player.y==2:
                            player.inv["BLcheers"]+=1
                    elif random_event() and encounter_cool<10:
                        res = battle(player, random_enemy(), "background2.png")
                        if res=="lose":
                            victory_screen(False)
                        encounter_cool = 44
        clock.tick(FPS)

if __name__=="__main__":
    main()