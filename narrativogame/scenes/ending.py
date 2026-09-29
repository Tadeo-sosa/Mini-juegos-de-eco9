import pygame, json, sys
from settings import WIDTH, HEIGHT, PALETTE
from engine.scene_manager import Scene
from engine.ui import Button

class EndingScene(Scene):
    def __init__(self, manager, state, audio):
        super().__init__(manager)
        self.state = state
        self.audio = audio
        self.font_big = pygame.font.SysFont("arial", 36)
        self.font = pygame.font.SysFont("arial", 22)
        with open("narrative/script.json", "r", encoding="utf-8") as f:
            self.script = json.load(f)

        self.text = ""
        self.input_cooldown = 0.2
        self.buttons = []

        # Fondo
        try:
            self.bg = pygame.image.load("assets/images/ending_bg.png").convert()
            self.bg = pygame.transform.smoothscale(self.bg, (WIDTH, HEIGHT))
        except Exception:
            self.bg = None

    def on_enter(self):
        # Texto según estadísticas
        if self.state.stats.get("bondad", 0) > 0:
            self.text = self.script["ending"]["kind"]
        else:
            self.text = self.script["ending"]["neutral"]

        self.audio.stop_ambience()

        # --- Botones ---
        btn_w, btn_h = 220, 48
        gap = 18
        y = HEIGHT - 80
        x_center = WIDTH // 2

        def go_title():
            # Import local para evitar import circular
            from scenes.title import TitleScene
            self.manager.replace(TitleScene(self.manager))

        def quit_game():
            pygame.quit()
            sys.exit(0)

        self.buttons = [
            Button(
                rect=(x_center - btn_w - gap//2, y, btn_w, btn_h),
                text="Volver al título",
                font=self.font,
                on_click=go_title
            ),
            Button(
                rect=(x_center + gap//2, y, btn_w, btn_h),
                text="Salir",
                font=self.font,
                on_click=quit_game
            ),
        ]

    def handle_event(self, event):
        if self.input_cooldown > 0:
            return
        # Pasar eventos a los botones
        for b in self.buttons:
            b.handle_event(event)
        # Fallback opcional: tecla suelta → volver al título
        if event.type == pygame.KEYUP:
            from scenes.title import TitleScene
            self.manager.replace(TitleScene(self.manager))

    def update(self, dt):
        if self.input_cooldown > 0:
            self.input_cooldown -= dt

    def draw(self):
        surf = self.manager.screen
        if self.bg:
            surf.blit(self.bg, (0, 0))
        else:
            surf.fill(PALETTE["bg"])

        # Título del final
        t1 = self.font_big.render("Fin (demo)", True, PALETTE["ink"])
        t1r = t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        surf.blit(t1, t1r)

        # Texto envuelto
        y = HEIGHT // 2 + 10
        wrapped, line = [], ""
        for word in self.text.split():
            test = (line + " " + word).strip()
            if len(test) > 60:
                wrapped.append(line)
                line = word
            else:
                line = test
        if line:
            wrapped.append(line)
        for i, s in enumerate(wrapped):
            tx = self.font.render(s, True, PALETTE["ink"])
            surf.blit(tx, (WIDTH // 2 - 280, y + i * 28))

        # Botones
        for b in self.buttons:
            b.draw(surf)
