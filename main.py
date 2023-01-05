import pygame
import random
from player import Player
import asyncio
from particle import Particle
import math
import pygame_shaders

import noise

pygame.init()
pygame.font.init()


class Game:
    def __init__(self):
        self.width = 800
        self.height = 800
        self.zoom = 4
        self.global_time = 0
        self.seed = random.randrange(-10000000, 100000000)

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL)
        self.display = pygame.Surface((self.width / self.zoom, self.height / self.zoom))
        self.display.set_colorkey((200, 200, 200))
        self.clock = pygame.time.Clock()
        self.offset = 0

        self.player = Player(self)

        self.font = pygame.font.Font("assets/font.ttf", 32)
        self.small_font = pygame.font.Font("assets/font.ttf", 10)

        self.score = 0
        self.particles = []

        self.bg = self.load_img("assets/images/mountain.png")
        self.cloud = self.load_img("assets/images/cloud.png")   
        self.objects = []

        self.current_score = -1
        self.text = ""

        pygame.mixer.music.load("assets/music/music-pygbag.ogg")
        pygame.mixer.music.play(-1)

        self.ding_sound = pygame.mixer.Sound("assets/music/pickupCoin-pygbag.ogg")
        self.ding_sound.set_volume(0.3)
        self.stop_sound = pygame.mixer.Sound("assets/music/hitHurt-pygbag.ogg")
        self.ding_sound.set_volume(0.3)
        self.death_sound = pygame.mixer.Sound("assets/music/hitHurt-pygbag.ogg")
        self.death_sound.set_volume(1.3)

        self.shader = pygame_shaders.Shader(size=(self.width, self.height), display=(self.width, self.height), 
                        pos=(0, 0), vertex_path="shaders/vertex.glsl", 
                        fragment_path="shaders/fragment.glsl", target_texture=self.display)

        self.bg = pygame.Surface((self.width, self.height))
        self.bg_shader = pygame_shaders.Shader(size=(self.width, self.height), display=(self.width, self.height), 
                        pos=(0, 0), vertex_path="shaders/vertex.glsl", 
                        fragment_path="shaders/bg_fragment.glsl", target_texture=self.bg)

        self.circles = []
        self.death_particles = []
        self.trails = []

    def load_img(self, path):
        img = pygame.image.load(path).convert()
        img.set_colorkey((255, 255, 255))
        return img

    async def main(self):

        while True:
            self.global_time += 1
            pygame_shaders.clear((255, 255, 255)) #Fill with the color you would like in the background
            self.display.fill((200, 200,200))
            for obj in self.objects:
                obj[0] -= 1
                self.display.blit(self.cloud, (obj[0] * obj[2], obj[1]))

            if self.score != self.current_score:
                self.text = self.font.render(str(round(self.score)), False, (0, 0, 0))
                self.current_score = self.score
            self.display.blit(self.text, self.text.get_rect(center=(800/self.zoom//2, 32)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit

                if not self.player.dead:
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            if self.player.rising:
                                self.player.launch = True
                                if self.player.velocity > 10.1:
                                    self.player.launch_velocity = self.player.velocity / 3
                                    self.player.launched_boost = True
                                else:
                                    self.player.launch_velocity = 0.5
                                    self.player.launched_boost = True


            self.tiles = [0] * 800 #hmm yes preallocation
            for x in range(self.width):
                if random.randrange(0, 500) == 1:
                    self.particles.append(Particle(pygame.Rect(x, 0, 2, 2), self))
                y = ((noise.pnoise2(x / self.width*2 + self.offset, self.seed, 3, 10) * self.height + 60) / 10) + 140
                rect = pygame.Rect((x//2)*2, y, 2, 2)
                pygame.draw.rect(self.display, (255, 255, 255), rect)
                self.tiles[x] = rect
                # if noise.pnoise2(x / self.width*2 + self.offset, self.seed^3236, 3, 10.001) > 0.3:
                    # self.objects.append([x,100])

            if random.randrange(0, 200) == 10:
                self.objects.append([800/self.zoom, random.randrange(0, 200), random.random()+1])

            self.player.update()

            for trail in self.trails:
                if trail[1] <= 0:
                    self.trails.remove(trail)
                trail[1] -= 1
                pygame.draw.rect(self.display, (240, 240, 240), trail[0])


            for part in self.death_particles:
                part[0].x += part[1].x
                part[0].y += part[1].y
                part[1].y += 0.5
                self.trails.append([part[0].copy(), 5])
                pygame.draw.rect(self.display, (240, 240, 240), part[0])
            

            if self.player.dead:
                died_text = self.font.render("Game Over", False, (0,0,0))
                self.display.blit(died_text,
                    died_text.get_rect(center=(self.width/self.zoom//2,self.height/self.zoom//2)))
                score_text = self.small_font.render(f"Final Score: {round(self.score)}", False, (0,0,0))
                self.display.blit(score_text,
                    score_text.get_rect(center=(self.width/self.zoom//2,self.height/self.zoom//2+32)))
                enter_text = self.small_font.render("Enter to restart...", False, (0,0,0))
                self.display.blit(enter_text,
                    enter_text.get_rect(center=(self.width/self.zoom//2,self.height/self.zoom//2+50)))

            for particle in self.particles:
                particle.update()

            for circle in self.circles:
                x = circle[0].x
                y = circle[0].y
                circle[1] += 4
                circle[2] -= 1
                pygame.draw.circle(self.display, (200, 200, 200), (x, y), circle[1], circle[2])

            self.bg_shader.send("time", [self.global_time/12])

            self.bg_shader.render(self.bg)
            self.shader.render(self.display)

            pygame.display.flip()
            self.screen.blit(pygame.transform.scale(self.display, (self.width, self.height)), (0, 0))
            self.clock.tick(60)
            pygame.display.set_caption(f"Skii!")

            await asyncio.sleep(0)

asyncio.run(Game().main())
