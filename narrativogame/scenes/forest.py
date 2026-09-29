import pygame
import json
from settings import WIDTH, HEIGHT, PALETTE
from engine.scene_manager import Scene
from engine.narrator import Narrator
from scenes.ending import EndingScene
from game.actor import Character, NPC
from scenes.electric import ElectricScene
from scenes.drones import DronesScene

class ForestScene(Scene):
    def __init__(self, manager, state, audio):
        super().__init__(manager)
        self.state = state
        self.audio = audio
        self.font = pygame.font.SysFont("arial", 22)
        self.narrator = Narrator(self.font)

        # Fondo del bosque (panorámico)
        try:
            self.bg = pygame.image.load("assets/images/forest_bg.png").convert()
        except Exception:
            self.bg = pygame.Surface((WIDTH, HEIGHT))
            self.bg.fill((224, 235, 228))
        self.bg = pygame.transform.smoothscale(self.bg, (1920, HEIGHT))
        self.camera_x = 0

        # Ignorar clics heredados al entrar
        self.input_cooldown = 0.5

        # Personajes
        self.player = Character(WIDTH // 2 - 120, HEIGHT - 110)
        self.npc = NPC(WIDTH // 2 + 140, HEIGHT - 120, name="guía")

        # Hotspots
        self.glitter = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 - 20, 40, 40)
        # zona de salida (subida para que no la tape el narrador)
        self.exit_zone = pygame.Rect(WIDTH - 84, HEIGHT - 100, 60, 60)

        # Sprite del brillo
        try:
            self.glitter_img = pygame.image.load("assets/images/forest_glitter.png").convert_alpha()
        except Exception:
            self.glitter_img = None

        # Icono de salida
        self.exit_img = None
        try:
            img = pygame.image.load("assets/images/exit_icon.png").convert_alpha()
            self.exit_img = pygame.transform.smoothscale(img, (self.exit_zone.w, self.exit_zone.h))
        except Exception:
            self.exit_img = None

        # Guion
        with open("narrative/script.json", "r", encoding="utf-8") as f:
            self.script = json.load(f)

    def on_enter(self):
        for line in self.script["forest_intro"]["lines"]:
            self.narrator.say(line)

    def handle_event(self, event):
        if self.input_cooldown > 0:
            return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Movimiento del personaje al clic
            self.player.move_to(*event.pos)

            # Interacciones
            if self.glitter.collidepoint(event.pos):
                self.state.add("bondad", 1)
                self.state.set_flag("vio_mariposa", True)
                self.narrator.say(self.script["kind_choice"]["good"])

            elif self.npc.rect.collidepoint(event.pos):
                self.state.add("curiosidad", 1)
                self.narrator.say("Narrador: El guía susurra un atajo entre los árboles.")

            elif self.exit_zone.collidepoint(event.pos):
                self.manager.replace(
                    ElectricScene(
                        self.manager,
                        self.state,
                        self.audio
                    )
                )
    

    def update(self, dt):
        if self.input_cooldown > 0:
            self.input_cooldown -= dt
        self.player.update(dt)
        self.narrator.update(dt)

    def draw(self):
        surf = self.manager.screen
        surf.blit(self.bg, (-self.camera_x, 0))

        # brillo
        if self.glitter_img:
            r = self.glitter_img.get_rect(center=self.glitter.center)
            surf.blit(self.glitter_img, r)
        # (si no hay imagen, no dibujamos el fallback para mantener estética)

        # icono de salida (si existe)
        if self.exit_img:
            surf.blit(self.exit_img, self.exit_zone.topleft)
        # (si querés debug visual, destapá el rectángulo)
        # pygame.draw.rect(surf, (200, 210, 220), self.exit_zone, 2, border_radius=8)

        # personajes
        self.npc.draw(surf)
        self.player.draw(surf)

        tip = self.font.render("Haz clic para caminar. Brillo / NPC / borde der. para salir.", True, PALETTE["ink"])
        surf.blit(tip, (20, 20))
        self.narrator.draw(surf)
