import sys

import pygame


class Settings:
    """A class to manage the game settings."""

    def __init__(self) -> None:
        """Initialize the game settings."""
        # Screen settings
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 500
        self.FPS = 60
        self.BG_COLOR = (42, 135, 191)

        # Player's settings
        self.player_speed = 5

        # Block's settings
        self.BLOCK_SIZE = 50
        self.BLOCK_COLOR = (18, 102, 79)

        # Limits how far the player can go to the left
        # or right side of the screen until it starts to shift
        self.LEFT_SCREEN_LIMIT = 100
        self.RIGHT_SCREEN_LIMIT = self.SCREEN_WIDTH - 200


class Block(pygame.sprite.Sprite):
    """A class to define each block that makes the level."""

    def __init__(self) -> None:
        """Initializes a block of a fixed size."""
        super().__init__()

        self.settings = Settings()
        self.color = self.settings.BLOCK_COLOR
        self.size = self.settings.BLOCK_SIZE

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.color)

        self.rect = self.image.get_rect()

    def set_position(self, x: int, y: int) -> None:
        """Updates the position of the block."""
        self.rect.x = x
        self.rect.y = y


class Level:
    """A generic super-class used to define a level."""

    def __init__(self, game: "Platformer") -> None:
        """Initializes all sprite groups of the level."""
        self.screen = game.screen
        self.settings = game.settings
        self.platform_list = pygame.sprite.Group()

        # Keeps track of how much has this level been
        # shifted left or right
        self.level_shift = 0

    def update(self) -> None:
        """Update everything in this level."""
        self.platform_list.update()

    def draw(self) -> None:
        """Draw everything on this level."""

        # Draw the background
        self.screen.fill(self.settings.BG_COLOR)

        # Draw all the sprites that we have
        self.platform_list.draw(self.screen)

    def create(self, pattern: list[str]) -> None:
        """Creates the structure of the level based on a string pattern."""
        current_x = 0
        current_y = self.settings.SCREEN_HEIGHT

        for row in pattern[::-1]:
            current_y -= self.settings.BLOCK_SIZE

            for object_type in row:
                if object_type == "X":
                    new_block = Block()
                    new_block.set_position(current_x, current_y)
                    self.platform_list.add(new_block)

                current_x += self.settings.BLOCK_SIZE

            current_x = 0

    def shift_level(self, shift_x: int) -> None:
        """Shifts the whole level right or left, depending of the player's movement."""
        # Keep track of the shift amount
        self.level_shift += shift_x

        # Shift all the level sprites
        for platform in self.platform_list:
            platform.rect.x += shift_x

        print(self.level_shift)


class Level_01(Level):
    """A class that defines the layout of level 1."""

    def __init__(self, game: "Platformer"):
        """Creates level 1 of the game."""
        super().__init__(game)

        self.level_limit = -1200

        # The level layout
        self.level = [
            "___________________XX__",
            "___XXXX____XXXXX",
            "",
            "",
            "XXXXXXXXXXXXXXXXXXXXXXX",
        ]

        self.create(self.level)


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
        self.rect.bottom = self.screen_rect.bottom - self.settings.BLOCK_SIZE
        self.rect.left = self.settings.LEFT_SCREEN_LIMIT

        # Movement flags
        self.moving_right = False
        self.moving_left = False
        self.on_ground = False

        # Speed of the player in the x and y axis; at the
        # start of the game the player doesn't move
        self.change_x = 0
        self.change_y = 0

        # List the of the level blocks
        self.level = None

    def update(self):
        """Update the robot's position based on its x and y speeds."""

        self._change_speed()
        self._apply_gravity()

        # Move the player left or right
        self.rect.x += self.change_x

        self._check_horizontal_collisions()

        # Assume the player isn't touching any platform
        self.on_ground = False

        # Move the player up or down
        self.rect.y += self.change_y

        self._check_vertical_collisions()

    def _apply_gravity(self) -> None:
        """Moves the player towards the bottom of the screen."""
        self.change_y += 0.6

    def jump(self) -> None:
        """Make the player jump by changing its vertical speed."""
        # If it is ok to jump, set our speed upwards
        if self.on_ground:
            self.change_y = -15
            self.on_ground = False  # Player is now in the air

    def draw_me(self) -> None:
        """Draw the robot at the current location."""
        self.screen.blit(self.image, self.rect)

    def _change_speed(self) -> None:
        """Determine horizontal speed based on movement flags."""
        if self.moving_left and not self.moving_right:
            self.change_x = -self.settings.player_speed
        elif self.moving_right and not self.moving_left:
            self.change_x = self.settings.player_speed
        else:
            # Player stops if both keys are pressed or no keys are pressed
            self.change_x = 0

    def _check_horizontal_collisions(self) -> None:
        """Check if the player hit anything in the x-axis. If so, update the position
        so it doesn't go through the object."""
        platform_hits = pygame.sprite.spritecollide(
            self, self.level.platform_list, False
        )
        for platform in platform_hits:
            # Player was moving right
            if self.change_x > 0:
                self.rect.right = platform.rect.left
            # Player was moving left
            elif self.change_x < 0:
                self.rect.left = platform.rect.right

    def _check_vertical_collisions(self) -> None:
        """Check if the player hit anything in the y-axis. If so, update the position
        so it doesn't go through the object."""
        platform_hits = pygame.sprite.spritecollide(
            self, self.level.platform_list, False
        )
        for platform in platform_hits:
            # Player was moving down
            if self.change_y > 0:
                self.rect.bottom = platform.rect.top
                self.on_ground = True  # Player landed on a block
            # Player was moving up
            elif self.change_y < 0:
                self.rect.top = platform.rect.bottom

            # Stop player's vertical movement
            self.change_y = 0


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

        # Create all the levels
        self.level_list: list[Level] = []
        self.level_list.append(Level_01(self))

        # Set the current level
        self.level_no = 0
        self.current_level = self.level_list[self.level_no]

        self.player.level = self.current_level

    def run_game(self) -> None:
        """Starts the main loop of the game."""

        while True:
            self._check_events()
            self.current_level.update()
            self.player.update()
            self._update_level_shift()
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
        elif event.key == pygame.K_SPACE:
            self.player.jump()

    def _check_keyup_events(self, event: pygame.event.Event) -> None:
        """Respond to key releases"""
        if event.key == pygame.K_RIGHT:
            self.player.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.player.moving_left = False

    def _update_level_shift(self) -> None:
        """Shifts the level according to the player's movement and screen limits."""
        # If the player gets near the right side of the screen, shift the level left (-x)
        if self.player.rect.right >= self.settings.RIGHT_SCREEN_LIMIT:
            diff = self.player.rect.right - self.settings.RIGHT_SCREEN_LIMIT
            self.player.rect.right = self.settings.RIGHT_SCREEN_LIMIT
            self.current_level.shift_level(-diff)

        # If the player gets near the left side, shift the
        # level to the right (+x)
        elif self.player.rect.left <= self.settings.LEFT_SCREEN_LIMIT:
            diff = self.settings.LEFT_SCREEN_LIMIT - self.player.rect.left
            self.player.rect.left = self.settings.LEFT_SCREEN_LIMIT
            self.current_level.shift_level(diff)

    def _update_screen(self) -> None:
        """Update all game elements and flip the screen."""
        self.current_level.draw()
        self.player.draw_me()
        pygame.display.flip()


if __name__ == "__main__":
    # Make an instance of the game and run it
    platformer = Platformer()
    platformer.run_game()
