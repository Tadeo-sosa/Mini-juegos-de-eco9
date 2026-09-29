import pygame

class Character:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.target = pygame.Vector2(x, y)
        self.speed = 140
        self.radius = 18
        self.sprite = None
        try:
            img = pygame.image.load("assets/images/hero_idle.png").convert_alpha()
            # escalar a 64x64 aprox para encajar
            self.sprite = pygame.transform.smoothscale(img, (64, 64))
        except Exception:
            self.sprite = None

    def move_to(self, x, y):
        self.target.update(x, y)

    def update(self, dt):
        delta = self.target - self.pos
        d = delta.length()
        if d > 1:
            step = min(self.speed * dt, d)
            self.pos += delta.normalize() * step

    def draw(self, surf):
        if self.sprite:
            r = self.sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surf.blit(self.sprite, r)
        else:
            pygame.draw.circle(surf, (145, 180, 170), (int(self.pos.x), int(self.pos.y)), self.radius)
            pygame.draw.circle(surf, (55, 65, 81), (int(self.pos.x), int(self.pos.y)), self.radius, 2)


class NPC:
    def __init__(self, x, y, w=40, h=60, name="npc"):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.name = name
        self.sprite = None
        try:
            img = pygame.image.load("assets/images/npc1.png").convert_alpha()
            self.sprite = pygame.transform.smoothscale(img, (64, 64))
        except Exception:
            self.sprite = None

    def draw(self, surf):
        if self.sprite:
            r = self.sprite.get_rect(center=self.rect.center)
            surf.blit(self.sprite, r)
        else:
            pygame.draw.rect(surf, (180, 160, 190), self.rect, border_radius=8)
            pygame.draw.rect(surf, (55, 65, 81), self.rect, 2, border_radius=8)
