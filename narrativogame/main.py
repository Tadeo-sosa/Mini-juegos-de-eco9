import pygame
import sys
from settings import WIDTH, HEIGHT, TITLE, FPS
from engine.scene_manager import SceneManager
from scenes.title import TitleScene

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    manager = SceneManager(screen)
    manager.push(TitleScene(manager))

    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            manager.handle_event(event)

        manager.update(dt)
        manager.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()