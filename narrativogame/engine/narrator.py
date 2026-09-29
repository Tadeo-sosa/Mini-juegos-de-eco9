import pygame
from settings import PALETTE
import time

class Narrator:
    """Narrador externo con subtítulos y beep de voz (placeholder).
    En un proyecto real, reemplazar por archivos de voz por línea.
    """
    def __init__(self, font):
        self.font = font
        self.queue = []
        self.active = None
        self.timer = 0.0
        self.beep = pygame.mixer.Sound("assets/audio/narrator_beep.wav")
        self.visible_time = 2.5  # segundos por línea (aprox)

    def say(self, text):
        self.queue.append(text)

    def clear(self):
        self.queue.clear()
        self.active = None
        self.timer = 0.0

    def update(self, dt):
        if not self.active and self.queue:
            self.active = self.queue.pop(0)
            self.timer = 0.0
            self.beep.play()
        if self.active:
            self.timer += dt
            if self.timer >= self.visible_time:
                self.active = None

    def draw(self, surf):
        if not self.active: return
        margin = 20
        text = self.active
        # caja semi-transparente
        w, h = surf.get_size()
        box = pygame.Surface((w, 80), pygame.SRCALPHA)
        box.fill((20, 20, 25, 150))
        surf.blit(box, (0, h - 90))
        # texto
        rendered = self.font.render(text, True, PALETTE["white"])
        surf.blit(rendered, (margin, h - 80))