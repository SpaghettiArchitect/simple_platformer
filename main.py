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

        # Player's settings
        self.player_speed = 5


class Player(pygame.sprite.Sprite):
    """A class to create and control the robot player."""

    def __init__(self, game: "Platformer") -> None:
        """Initialize the robot player and its position"""
        super().__init__()

        self.screen = game.screen
        self.settings = game.settings
        self.screen_rect = game.screen.get_rect()

        # Load the robot image and get its rect
        self.image = pygame.image.load(r"assets/robot.png").convert_alpha()
        self.rect = self.image.get_rect()

        # Start the player at the bottom-left of the screen
        self.rect.bottomleft = self.screen_rect.bottomleft

        # Moving flags; at the start of the game the robot doesn't move
        self.moving_right = False
        self.moving_left = False

        # Sets the gravity at the start of the game
        self.gravity = 0

    def update(self):
        """Update the robot's position based on the movement flags."""

        self.apply_gravity()

        # Update the robot's x value, no the rect
        if self.moving_right and self.rect.right <= self.screen_rect.right:
            self.rect.x += self.settings.player_speed
        if self.moving_left and self.rect.left >= 0:
            self.rect.x -= self.settings.player_speed

    def apply_gravity(self) -> None:
        """Moves the player towards the bottom of the screen."""
        self.gravity += 1
        self.rect.y += self.gravity

        if self.rect.bottom >= self.screen_rect.bottom:
            self.rect.bottom = self.screen_rect.bottom
            self.gravity = 0

    def jump(self) -> None:
        """Reduces the gravity, causing the player to jump."""
        self.gravity = -20

    def draw_me(self) -> None:
        """Draw the robot at the current location."""
        self.screen.blit(self.image, self.rect)


class Platformer:
    """The main platformer class, use to create and run the game."""

    def __init__(self) -> None:
        """Initialize the game an create all resorces needed."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        # Creates the window and sets the caption
        self.screen = pygame.display.set_mode(
            (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Robot Platfomer")

        # Creates the robot the player can control
        self.player = Player(self)

    def run_game(self) -> None:
        """Starts the main loop of the game."""

        while True:
            self._check_events()
            self.player.update()
            self._update_screen()
            self.clock.tick(self.settings.FPS)

    def _check_events(self) -> None:
        """Check and respond to all keypresses events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event: pygame.event.Event) -> None:
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.player.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.player.moving_left = True
        elif (
            event.key == pygame.K_SPACE
            and self.player.rect.bottom >= self.screen.get_rect().bottom
        ):
            self.player.jump()

    def _check_keyup_events(self, event: pygame.event.Event) -> None:
        """Respond to key releases"""
        if event.key == pygame.K_RIGHT:
            self.player.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.player.moving_left = False

    def _update_screen(self) -> None:
        """Update all game elements and flip the screen."""
        self.screen.fill(self.settings.BG_COLOR)
        self.player.draw_me()
        pygame.display.flip()


if __name__ == "__main__":
    # Make an instance of the game and run it
    platformer = Platformer()
    platformer.run_game()
