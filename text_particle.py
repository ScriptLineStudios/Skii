import pygame

class TextParticle:
    def __init__(self, pos, game, text):
        self.pos = pos
        self.game = game
        self.text = text
        
    def update(self):
        text = self.game.small_font.render(self.text, False, (0, 0, 0))
        self.pos.y -= 2
        self.game.display.blit(text, self.pos)
