import pygame
from settings import PALETTE

class Scene:
    def __init__(self, manager):
        self.manager = manager
    def on_enter(self): pass
    def on_exit(self): pass
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self): pass

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.stack = []

    def push(self, scene):
        if self.stack:
            self.stack[-1].on_exit()
        self.stack.append(scene)
        scene.on_enter()

    def pop(self):
        if self.stack:
            self.stack[-1].on_exit()
            self.stack.pop()
            if self.stack:
                self.stack[-1].on_enter()

    def replace(self, scene):
        self.pop()
        self.push(scene)

    def current(self):
        return self.stack[-1] if self.stack else None

    def handle_event(self, event):
        # ✅ Delegar los eventos a la escena actual; NO cerrar el juego aquí
        if self.current():
            self.current().handle_event(event)

    def update(self, dt):
        if self.current():
            self.current().update(dt)

    def draw(self):
        if self.current():
            self.current().draw()
        else:
            self.screen.fill(PALETTE["bg"])
