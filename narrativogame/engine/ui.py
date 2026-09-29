import pygame
from settings import PALETTE

class Button:
    def __init__(self, rect, text, font, on_click):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.hover = False
        self.pressed = False
        # skin opcional desde assets/ui_button.png
        self.skin = None
        try:
            img = pygame.image.load("assets/ui_button.png").convert_alpha()
            self.skin = pygame.transform.smoothscale(img, (self.rect.w, self.rect.h))
        except Exception:
            self.skin = None

    def handle_event(self, event, audio=None):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                if audio:
                    audio.play_click()
                if self.on_click:
                    self.on_click()
            self.pressed = False

    def draw(self, surf):
        if self.skin:
            surf.blit(self.skin, self.rect.topleft)
        else:
            color = PALETTE["accent2"] if self.hover else PALETTE["accent"]
            pygame.draw.rect(surf, color, self.rect, border_radius=14)
            pygame.draw.rect(surf, PALETTE["shadow"], self.rect, width=2, border_radius=14)
        txt = self.font.render(self.text, True, (255, 255, 255))
        txtr = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txtr)
