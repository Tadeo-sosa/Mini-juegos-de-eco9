import pygame

class Audio:
    def __init__(self):
        self.sfx_click = pygame.mixer.Sound("assets/audio/ui_click.wav")
        self.ambience = pygame.mixer.Sound("assets/audio/ambience_loop.wav")
        self.ambience.set_volume(0.15)

    def play_click(self):
        self.sfx_click.play()

    def play_ambience(self):
        # reproducir en loop
        self.ambience.play(loops=-1)

    def stop_ambience(self):
        self.ambience.stop()