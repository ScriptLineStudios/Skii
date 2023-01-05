import pygame
import random
import math

class Particle:
    def __init__(self, pos, game, vel=pygame.Vector2(0, 2), fall=False, color=(255, 255,255)):
        self.pos = pos
        self.game = game
        self.lifetime = 100
        self.vel = vel
        self.fall = fall
        self.speed = random.randrange(1, 4)
        self.color = color
        
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.game.particles.remove(self)
        if self.fall:
            self.vel.y += self.speed / 2
        self.pos.y += self.vel.y
        self.pos.x += self.vel.x

        pygame.draw.rect(self.game.display, self.color, self.pos)