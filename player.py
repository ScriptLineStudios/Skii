import pygame
from text_particle import TextParticle
from particle import Particle
import random
import pygame_shaders


class Player:
    def __init__(self, game):
        self.movement = pygame.Vector2(0, 0)
        self.rect = pygame.Rect((40, 10, 16, 16))
        self.game = game
        self.time = 0
        self.time_count = 1
        self.check_range = range(40, 45)
        self.rising = False
        self.launch = False
        self.velocity = 0
        self.launch_velocity = 0
        self.airtime = 0
        self.cooldown = 0
        self.launched_boost = False
        self.zoom_time = 0
        self.zoom = 4
        self.images = [self.game.load_img("assets/images/player1.png"), self.game.load_img("assets/images/player2.png"), self.game.load_img("assets/images/player3.png")]
        self.angle = 0
        self.img_index = 0
        self.anim_time = 10
        self.sliding = 0
        self.steepness = 0
        self.boost = 0
        self.dead = False
        self.zoom_back = False

    def get_colliding_tiles(self):
        collisions = []
        indices = []
        for i in self.check_range:
            tile = self.game.tiles[i]
            if tile.colliderect(self.rect):

                if self.launch and self.airtime > 20:
                    self.zoom_back = True
                    for i in range(10):
                                self.game.death_particles.append([pygame.Rect(self.rect.x, self.rect.y, 2, 2), pygame.Vector2(random.randrange(-5,5), -random.randrange(1, 6))])
                    self.sliding = 200
                    self.launch = False
                    self.airtime = 0
                    self.angle = 0
                    if not self.rising:
                        self.boost += 0.001
                        self.game.ding_sound.play()
                        self.game.particles.append(TextParticle(self.rect.copy(), self.game, f"x{self.boost*100}!"))

                    else:
                        # if self.boost >= 0.003:
                        #     self.game.particles.append(TextParticle(self.rect.copy(), self.game, f"):"))
                        # else:
                        if self.steepness > 1.1:
                            self.game.death_sound.play()
                            for i in range(40):
                                self.game.death_particles.append([pygame.Rect(self.rect.x, self.rect.y, 2, 2), pygame.Vector2(random.randrange(-5,5), -random.randrange(1, 6))])
                            self.dead = True
                        #self.boost = 0

                collisions.append(tile)
        return collisions, indices

    def move(self):
        self.rect.x += self.movement.x
        self.rect.y += self.movement.y

        for tile in self.get_colliding_tiles()[0]:
            self.rect.bottom = tile.top


    def update(self):
        self.img_index += 1
        if self.img_index + 1 >= len(self.images) * self.anim_time:
            self.img_index = 0

        if self.airtime > 20 and not self.dead:
            self.game.score += 0.1 + (self.boost*100) 

        if self.zoom_back:
            if self.game.zoom < 4:
                self.game.zoom += 0.3
                self.game.display = pygame.transform.scale(self.game.display, (self.game.width / self.game.zoom, self.game.height / self.game.zoom))
                self.game.shader = pygame_shaders.Shader(size=(self.game.width, self.game.height), display=(self.game.width, self.game.height), 
                        pos=(0, 0), vertex_path="shaders/vertex.glsl", 
                        fragment_path="shaders/fragment.glsl", target_texture=self.game.display)
            else:
                self.zoom_back = False

        self.movement = pygame.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if not self.dead:
            if keys[pygame.K_SPACE]:
                if not self.dead:
                    if self.airtime == 0:
                        self.game.offset += 0.005 + self.boost
                    else:
                        self.angle -= 2
                        self.movement.y += 4

        if keys[pygame.K_RETURN]:
            self.dead = False
            self.game.score = 0
            self.game.current_score = -1

        avg_height = sum([self.game.tiles[x].y for x in self.check_range]) / len(self.check_range) #doing a bit of sampling magic
        right_height = sum([self.game.tiles[x+len(self.check_range)].y for x in self.check_range]) / len(self.check_range)

        self.velocity = (avg_height / (right_height) * 10)
        self.rising = avg_height > right_height
        
        _avg_height = sum([self.game.tiles[x].y for x in self.check_range]) / len(self.check_range)
        _right_height = sum([self.game.tiles[x+len(range(40, 80))].y for x in range(40, 80)]) / len(range(40, 80))
        
        self.steepness = _avg_height / _right_height

        if self.launch:
            #if self.airtime > 10:
            #    self.angle += 4
            if self.rect.y < 25:
                if self.game.zoom > 2-self.rect.y/512:
                    self.game.zoom -= 0.3
                    self.game.display = pygame.transform.scale(self.game.display, (self.game.width / self.game.zoom, self.game.height / self.game.zoom))
                    self.game.shader = pygame_shaders.Shader(size=(self.game.width, self.game.height), display=(self.game.width, self.game.height), 
                        pos=(0, 0), vertex_path="shaders/vertex.glsl", 
                        fragment_path="shaders/fragment.glsl", target_texture=self.game.display)
                else:
                    self.zoom_time -= 1
            self.game.offset += 0.005 + self.boost
            if self.time <= 0:
                if not keys[pygame.K_SPACE]:
                    self.movement.y -= self.launch_velocity + self.boost*500
                if self.cooldown <= 0:
                    self.launch_velocity -= 0.4
                    self.cooldown = 2
                else:
                    self.cooldown -= 1
                self.time = 1
            else:
                self.time -= 1
            self.airtime += 1
        else:
            if self.sliding > 0:
                self.game.offset += self.sliding / 50000 + self.boost
                self.sliding -= 1
                if self.sliding == 120 and not keys[pygame.K_SPACE]:
                    self.game.stop_sound.play()
                    self.game.particles.append(TextParticle(self.rect.copy(), self.game, f":("))
                    self.boost = 0
            if self.rising:
                self.angle = 6
            else:
                self.angle = 0
            self.movement.y += 4


        self.move() 
        self.game.display.blit(pygame.transform.rotate(self.images[self.img_index // self.anim_time], self.angle), self.rect)