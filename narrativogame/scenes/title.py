import pygame
from settings import WIDTH, HEIGHT, PALETTE
from engine.scene_manager import Scene
from engine.narrator import Narrator
from engine.audio import Audio
from engine.ui import Button
from scenes.forest import ForestScene
from game.state import GameState

class TitleScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.font_big = pygame.font.SysFont("arial", 42)
        self.font = pygame.font.SysFont("arial", 24)
        self.narrator = Narrator(self.font)
        self.audio = Audio()
        self.buttons = []
        self.state = GameState()

        # Fondo (opcional): si existe assets/images/title_bg.png lo usa
        self.bg = None
        try:
            img = pygame.image.load("assets/images/title_bg.png").convert()
            self.bg = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))
        except Exception:
            self.bg = None  # fallback: color plano en draw()

    def on_enter(self):
        self.audio.play_ambience()
        self.narrator.say("Narrador: Bienvenida a 'Pequeña Fortuna'.")
        self.narrator.say("Narrador: Un paseo breve, decisiones suaves.")

        btn_w, btn_h = 220, 48
        start_btn = Button(
            rect=(WIDTH // 2 - btn_w // 2, HEIGHT // 2, btn_w, btn_h),
            text="Comenzar",
            font=self.font,
            on_click=lambda: self.manager.replace(ForestScene(self.manager, self.state, self.audio))
        )
        self.buttons = [start_btn]

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event, audio=self.audio)

    def update(self, dt):
        self.narrator.update(dt)

    def draw(self):
        surf = self.manager.screen
        if self.bg:
            surf.blit(self.bg, (0, 0))
        else:
            surf.fill(PALETTE["bg"])

        title = self.font_big.render("Pequeña Fortuna (demo)", True, PALETTE["ink"])
        tr = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        surf.blit(title, tr)

        for b in self.buttons:
            b.draw(surf)

        self.narrator.draw(surf)
