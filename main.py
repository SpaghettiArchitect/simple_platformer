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
        self.BG_COLOR = pygame.Color(42, 135, 191)

        # Player's settings
        self.player_speed = 5

        # Block's settings
        self.BLOCK_SIZE = 50
        self.BLOCK_COLOR = pygame.Color(18, 102, 79)

        # Enemies' settings
        self.enemy_speed = 3

        # Limits how far the player can go to the left
        # or right side of the screen until it starts to shift
        self.LEFT_SCREEN_LIMIT = 100
        self.RIGHT_SCREEN_LIMIT = self.SCREEN_WIDTH - 200


class Block(pygame.sprite.Sprite):
    """A class to define each block that makes the level."""

    def __init__(self, color: pygame.Color = None, pattern: bool = True) -> None:
        """Initializes a block of a fixed size."""
        super().__init__()

        self.settings = Settings()

        if not color:
            self.color = self.settings.BLOCK_COLOR
        else:
            self.color = color

        self.size = self.settings.BLOCK_SIZE
        self.image = pygame.Surface((self.size, self.size))
        self.rect = self.image.get_rect()

        if pattern:
            self._draw_pattern()
        else:
            self.image.fill(self.color)

    def set_position(self, x: int, y: int) -> None:
        """Updates the position of the block."""
        self.rect.bottomleft = (x, y)

    def _draw_pattern(self) -> None:
        """Draws a triangular pattern inside the block."""
        # Top triangle
        pygame.draw.polygon(
            self.image,
            (self.color.r + 10, self.color.g + 10, self.color.b + 10),
            (self.rect.topleft, self.rect.topright, self.rect.center),
        )
        # Right triangle
        pygame.draw.polygon(
            self.image,
            self.color,
            (self.rect.topright, self.rect.bottomright, self.rect.center),
        )
        # Bottom triangle
        pygame.draw.polygon(
            self.image,
            (self.color.r - 10, self.color.g - 10, self.color.b - 10),
            (self.rect.bottomleft, self.rect.bottomright, self.rect.center),
        )
        # Left triangle
        pygame.draw.polygon(
            self.image,
            (self.color.r - 5, self.color.g - 5, self.color.b - 5),
            (self.rect.bottomleft, self.rect.topleft, self.rect.center),
        )


class Enemy(pygame.sprite.Sprite):
    """A class to create and control an enemy."""

    def __init__(self):
        """Initializes the enemy image and rect."""
        super().__init__()

        self.settings = Settings()
        self.image = pygame.image.load(r"assets\monster.png").convert_alpha()
        self.rect = self.image.get_rect()

        # Used for collision detection with the player
        self.mask = pygame.mask.from_surface(self.image)

        # Set the current direction of the enemy
        self.change_x = self.settings.enemy_speed

    def update(self, platform_limits: pygame.sprite.Group):
        """Updates the position of the enemy."""
        # Moves the enemy right or left on the platform
        self.rect.x += self.change_x

        # Check for collisions with any platform limit
        limit_hits = pygame.sprite.spritecollideany(self, platform_limits)
        if limit_hits is not None:
            self.image = pygame.transform.flip(self.image, True, False)
            self.change_x *= -1  # Change direction of movement

    def set_position(self, x: int, y: int) -> None:
        """Set the position of the enemy on the screen."""
        self.rect.bottomleft = (x, y)


class Level:
    """A generic super-class used to define a level."""

    def __init__(self, game: "Platformer") -> None:
        """Initializes all sprite groups of the level."""
        self.screen = game.screen
        self.settings = game.settings

        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.platform_limits = pygame.sprite.Group()

        # Keeps track of the starting position of the player
        self.player_pos = pygame.Vector2(0, 0)

        # Keeps track of how much has this level been
        # shifted left or right
        self.level_shift = 0

    def update(self) -> None:
        """Update everything in this level."""
        self.platforms.update()
        self.platform_limits.update()
        self.enemies.update(self.platform_limits)

    def draw(self) -> None:
        """Draw everything on this level."""

        # Draw the background
        self.screen.fill(self.settings.BG_COLOR)

        # Draw all the sprites that we have
        self.platforms.draw(self.screen)
        self.platform_limits.draw(self.screen)
        self.enemies.draw(self.screen)

    def create(self, pattern: list[str], level_size: int) -> None:
        """Creates the structure of the level based on a string pattern."""
        current_x = 0
        current_y = self.settings.SCREEN_HEIGHT

        # Add the platforms starting from the bottom-left of the screen
        for row in pattern[::-1]:
            for object_type in row:
                if object_type == "X":
                    new_block = Block()
                    new_block.set_position(current_x, current_y)
                    self.platforms.add(new_block)
                elif object_type == "P":
                    self.player_pos = pygame.Vector2(current_x, current_y)
                elif object_type == "E":
                    new_enemy = Enemy()
                    new_enemy.set_position(current_x, current_y)
                    self.enemies.add(new_enemy)
                elif object_type == "#":
                    new_platform_limit = Block(self.settings.BG_COLOR, False)
                    new_platform_limit.set_position(current_x, current_y)
                    self.platform_limits.add(new_platform_limit)

                current_x += self.settings.BLOCK_SIZE

            current_y -= self.settings.BLOCK_SIZE

            current_x = 0

        # Add the blocks that confine the player to the level
        self._add_limits(level_size)

    def _add_limits(self, level_size: int) -> None:
        """Add blocks to the left and right side to define the level's boundaries."""
        left_padding = self.settings.LEFT_SCREEN_LIMIT
        right_padding = self.settings.RIGHT_SCREEN_LIMIT
        screen_height = self.settings.SCREEN_HEIGHT
        block_size = self.settings.BLOCK_SIZE

        # Add the left padding of blocks to the level
        for current_y in range(screen_height, 0, -block_size):
            for current_x in range(-left_padding, 0, block_size):
                new_block = Block()
                new_block.set_position(current_x, current_y)
                self.platforms.add(new_block)

        # Add the right padding of blocks to the level
        for current_y in range(screen_height, 0, -block_size):
            for current_x in range(level_size, level_size + right_padding, block_size):
                new_block = Block()
                new_block.set_position(current_x, current_y)
                self.platforms.add(new_block)

    def shift_level(self, shift_x: int) -> None:
        """Shifts the whole level right or left, depending of the player's movement."""
        # Keep track of the shift amount
        self.level_shift += shift_x
        self.player_pos.x += shift_x

        # Shift all the level sprites
        for platform in self.platforms:
            platform.rect.x += shift_x

        for enemy in self.enemies:
            enemy.rect.x += shift_x

        for limit in self.platform_limits:
            limit.rect.x += shift_x


class Level_01(Level):
    """A class that defines the layout of level 1."""

    def __init__(self, game: "Platformer"):
        """Creates level 1 of the game."""
        super().__init__(game)

        # The level layout
        self.level = [
            "__#__E_#__#__E__#__XX__",
            "___XXXX____XXXXX",
            "",
            "P",
            "XXXXXXXXXXXXXXXXXXXXXXX",
        ]

        self.level_size = self.settings.BLOCK_SIZE * len(self.level[-1])

        self.create(self.level, self.level_size)


class Player(pygame.sprite.Sprite):
    """A class to create and control the robot player."""

    def __init__(self, game: "Platformer") -> None:
        """Initialize the robot player and its position"""
        super().__init__()

        self.screen = game.screen
        self.settings = game.settings

        # Load the robot image and get its rect
        self.image = pygame.image.load(r"assets/robot.png").convert_alpha()
        self.rect = self.image.get_rect()

        # Used for collision detection with enemies
        self.mask = pygame.mask.from_surface(self.image)

        # Movement flags
        self.moving_right = False
        self.moving_left = False
        self.on_ground = False

        # Speed of the player in the x and y axis; at the start of the game the
        # player doesn't move
        self.change_x = 0
        self.change_y = 0

        # Needed to access the level's platforms
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

    def set_position(self, coord: pygame.Vector2) -> None:
        """Set the position of the player on the screen."""
        self.rect.bottomleft = coord

    def _apply_gravity(self) -> None:
        """Moves the player towards the bottom of the screen."""
        self.change_y += 0.6

    def jump(self) -> None:
        """Make the player jump by changing its vertical speed."""
        # If it is ok to jump, set our speed upwards
        if self.on_ground:
            self.change_y = -14
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
        platform_hits = pygame.sprite.spritecollide(self, self.level.platforms, False)
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
        platform_hits = pygame.sprite.spritecollide(self, self.level.platforms, False)
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
        self.player_group = pygame.sprite.GroupSingle(self.player)

        # Create all the levels
        self.level_list: list[Level] = []
        self.level_list.append(Level_01(self))

        # Set the current level
        self.level_no = 0
        self.current_level = self.level_list[self.level_no]

        # The player needs the current level to now if it's colliding with
        # a platform
        self.player.level = self.current_level

        # Set the player position at the start of the game
        self.player.set_position(self.current_level.player_pos)

    def run_game(self) -> None:
        """Starts the main loop of the game."""

        while True:
            self._check_events()
            self.current_level.update()
            self.player.update()
            self._update_level_shift()
            self._check_player_enemy_collisions()
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

    def _check_player_enemy_collisions(self) -> None:
        """Checks if the player has collided with any enemy using masks.

        If the player is falling down and collides with the top of the enemy
        mask, the enemy is deleted and the player bounces a little.

        If the player touches any other part of the enemy, the player loses a
        life and its position is restarted to the start of the level.
        """
        enemy_hit = pygame.sprite.spritecollideany(
            self.player, self.current_level.enemies
        )

        if enemy_hit is not None:
            point_of_collision = pygame.sprite.collide_mask(enemy_hit, self.player)
            if point_of_collision is not None:
                if point_of_collision[1] <= 15 and self.player.change_y > 0:
                    self.player.change_y = -6
                    enemy_hit.kill()
                else:
                    self.player.set_position(self.current_level.player_pos)

    def _update_level_shift(self) -> None:
        """Shifts the level according to the player's movement and screen limits."""
        # If the player gets near the right side of the screen, shift the
        # level left (-x)
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
