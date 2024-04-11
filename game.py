import os
import sys
import math
import random

import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Chronoshift')
        self.screen = pygame.display.set_mode((1920, 1080)) #chg pour avoir en plein écran
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            'spikes': load_images('tiles/spikes'),
        }
        
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.level = 0
        self.load_level(self.level)
        
        self.screenshake = 0
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)

        # Font
        self.font = pygame.font.Font(None, 36)
    # Function to display text on the screen
    def draw_text(self, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)
        
    # Main menu loop
    def main_menu(self):
        loop=True
        while loop:
            self.screen.fill(self.WHITE)
            self.draw_text("Main Menu", self.font, self.BLACK, 1920 // 2, 100)
            
            # Buttons
            start_button = pygame.Rect((1920-200) // 2, 200, 200, 50)
            pygame.draw.rect(self.screen, self.RED, start_button)
            self.draw_text("Start", self.font, self.WHITE, start_button.centerx, start_button.centery)
            
            options_button = pygame.Rect((1920-200) // 2, 300, 200, 50)
            pygame.draw.rect(self.screen, self.RED, options_button)
            self.draw_text("Options", self.font, self.WHITE, options_button.centerx, options_button.centery)
            
            quit_button = pygame.Rect((1920-200) // 2, 400, 200, 50)
            pygame.draw.rect(self.screen, self.RED, quit_button)
            self.draw_text("Quit", self.font, self.WHITE, quit_button.centerx, quit_button.centery)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        print("Start button clicked")
                        self.sfx['shoot'].play()
                        loop=False
                    elif options_button.collidepoint(event.pos):
                        self.options_menu()
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                        
    # Options menu loop
    def options_menu(self):
        loop = True
        while loop:
            self.screen.fill(self.WHITE)
            self.draw_text("Options Menu", self.font, self.BLACK, 1920 // 2, 100)
            
            # Buttons
            keybinds_button = pygame.Rect(300, 200, 200, 50)
            pygame.draw.rect(self.screen, self.RED, keybinds_button)
            self.draw_text("Keybinds", self.font, self.WHITE, keybinds_button.centerx, keybinds_button.centery)
            
            video_button = pygame.Rect(300, 300, 200, 50)
            pygame.draw.rect(self.screen, self.RED, video_button)
            self.draw_text("Video", self.font, self.WHITE, video_button.centerx, video_button.centery)
            
            back_button = pygame.Rect(300, 400, 200, 50)
            pygame.draw.rect(self.screen, self.RED, back_button)
            self.draw_text("Back", self.font, self.WHITE, back_button.centerx, back_button.centery)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if keybinds_button.collidepoint(event.pos):
                        print("Keybinds button clicked")
                        self.keybinds_menu()
                        # Add your keybinds logic here
                    elif video_button.collidepoint(event.pos):
                        print("Video button clicked")
                        # Add your video settings logic here
                    elif back_button.collidepoint(event.pos):
                        loop = False
                        
    def change_key_binding(self, action):
        global key_bindings
        waiting_for_key = True
        while waiting_for_key:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    key_bindings[action] = event.key
                    waiting_for_key = False
                    print(f"Key for {action} changed to {pygame.key.name(event.key)}")
                    return
    def keybinds_menu(self):
        loop = True
        while loop:
            self.screen.fill(self.WHITE)
            self.draw_text("Options keybinds", self.font, self.BLACK, 1920 // 2, 50)

            mouvingupbutton = pygame.Rect(300, 400, 200, 50)
            pygame.draw.rect(self.screen, self.RED, mouvingupbutton)
            self.draw_text("up", self.font, self.WHITE, mouvingupbutton.centerx, mouvingupbutton.centery)


            mouvingdownbutton = pygame.Rect(300, 300, 200, 50)
            pygame.draw.rect(self.screen, self.RED, mouvingdownbutton)
            self.draw_text("down", self.font, self.WHITE, mouvingdownbutton.centerx, mouvingdownbutton.centery)


            mouvingleftbutton = pygame.Rect(300, 200, 200, 50)
            pygame.draw.rect(self.screen, self.RED, mouvingleftbutton)
            self.draw_text("left", self.font, self.WHITE, mouvingleftbutton.centerx, mouvingleftbutton.centery)


            mouvingrightbutton = pygame.Rect(300, 100, 200, 50)
            pygame.draw.rect(self.screen, self.RED, mouvingrightbutton)
            self.draw_text("right", self.font, self.WHITE, mouvingrightbutton.centerx, mouvingrightbutton.centery)


            dashbutton = pygame.Rect(100, 400, 200, 50)
            pygame.draw.rect(self.screen, self.RED, dashbutton)
            self.draw_text("dash", self.font, self.WHITE, dashbutton.centerx, dashbutton.centery)


            rewindbutton = pygame.Rect(100, 200, 200, 50)
            pygame.draw.rect(self.screen, self.RED, rewindbutton)
            self.draw_text("rewind", self.font, self.WHITE, rewindbutton.centerx, rewindbutton.centery)


            jumpbutton = pygame.Rect(100, 300, 200, 50)
            pygame.draw.rect(self.screen, self.RED, jumpbutton)
            self.draw_text("jump", self.font, self.WHITE, jumpbutton.centerx, jumpbutton.centery)

            back_button = pygame.Rect(300, 500, 200, 50)
            pygame.draw.rect(self.screen, self.RED, back_button)
            self.draw_text("Back", self.font, self.WHITE, back_button.centerx, back_button.centery)

            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if mouvingupbutton.collidepoint(event.pos):
                        
                        print("moving up  button clicked")

                    elif back_button.collidepoint(event.pos):
                        loop = False

                
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
            
        self.projectiles = []
        self.particles = [] 
        self.sparks = []
        self.bg_color = (14,219,248)
        self.ChronoState = 1
        self.recallState = 0
        
        self.scroll = [0, 0]
        
        self.transition = -30
        
        
    def run(self):
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
        self.sfx['ambience'].play(-1)
        
        while True:
            self.display.fill(self.bg_color)
            # self.display_2.blit(self.assets['background'], (0, 0))
            
            self.screenshake = max(0, self.screenshake - 1)
            
            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1
            
            if self.player.dead:
                if self.player.dead == 1: 
                    self.player.recall_pos = []
                    self.sfx['hit'].play()
                    for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                #chg fin des particules
                self.player.dead += 1
                if self.player.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.player.dead > 40:
                    self.load_level(self.level)
                    self.player.dead = 0
                    
            
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            
            
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            
            self.clouds.update(self.ChronoState)
            self.clouds.render(self.display_2, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)
            
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
            
            if not self.player.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)
            
            
            
            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]): #chg il y avait les particules dans cette condition je crois
                        self.projectiles.remove(projectile)
                        self.player.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
                    
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)
            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_r:
                        self.recallState = 1
                        self.ChronoState = -2
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_r:
                        self.recallState = 0
                        self.ChronoState = 1
                print(self.recallState)
                print(len(self.player.recall_pos))
                print(self.player.recall_index)
                if self.recallState == 1 and len(self.player.recall_pos) == 30 and self.player.recall_index >= 0:
                    print("sucess")
                    self.bg_color = (30,30,30)
                    self.player.recall()
                    if self.player.recall_index == 0:
                        self.player.recall_pos = []
                else:
                    self.player.time_pos()
                    self.bg_color = (14,219,248)
                    self.player.recall_index = 29
                
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))
                
            self.display_2.blit(self.display, (0, 0))
            
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

Game().main_menu()
Game().run()