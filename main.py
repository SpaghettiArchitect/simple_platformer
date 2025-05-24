import sys

import pygame


class Settings:
    """A class to manage the game settings."""

    def __init__(self) -> None:
        """Initialize the game settings."""
        # Screen settings
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.FPS = 60
        self.BG_COLOR = (42, 135, 191)


class Platformer:
    """The main platformer class, use to create and run the game."""

    def __init__(self) -> None:
        """Initialize the game an create all resorces needed."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Robot Platfomer")

    def run_game(self) -> None:
        """Starts the main loop of the game."""

        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(self.settings.FPS)

    def _check_events(self) -> None:
        """Check and respond to all keypresses events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    def _update_screen(self) -> None:
        """Update all game elements and flip the screen."""
        self.screen.fill(self.settings.BG_COLOR)
        pygame.display.flip()


if __name__ == "__main__":
    # Make an instance of the game and run it
    platformer = Platformer()
    platformer.run_game()
