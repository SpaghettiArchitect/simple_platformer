import sys

import pygame
from pygame import Color, Surface, Vector2
from pygame.sprite import Group, Sprite


class Settings:
    """A class to manage the game settings."""

    def __init__(self):
        """Initialize the game settings."""
        # Screen settings
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 500
        self.FPS = 60
        self.BG_COLOR = Color(42, 135, 191)

        # Player's settings
        self.player_speed = 5
        self.PLAYER_LIVES = 5

        # Block's settings
        self.BLOCK_SIZE = 50
        self.BLOCK_COLOR = Color(18, 102, 79)

        # Enemies' settings
        self.enemy_speed = 3
        self.ENEMY_POINTS = 100

        # Font settings
        self.FONT_COLOR = Color(255, 255, 255)

        # Limits how far the player can go to the left
        # or right side of the screen until it starts to shift
        self.LEFT_SCREEN_LIMIT = 100
        self.RIGHT_SCREEN_LIMIT = self.SCREEN_WIDTH - 200


class GameStats:
    """Class to keep track of the Platformer's statistics."""

    def __init__(self, settings: Settings):
        """Initialize the game's statistics."""
        self.settings = settings
        self.reset_statistics()

    def reset_statistics(self) -> None:
        """Initialize statistics that change during game execution."""
        self.lives_left = self.settings.PLAYER_LIVES
        self.score = 0
        self.level = 0


class Scoreboard:
    """Class to show scoring information to the player."""

    def __init__(
        self,
        screen: Surface,
        settings: Settings,
        stats: GameStats,
    ):
        """Initialize all scorekeeping attributes."""
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.settings = settings
        self.stats = stats

        self.screen_padding = 10

        # Font settings to display information
        self.text_color = self.settings.FONT_COLOR
        self.text_font = pygame.font.SysFont(None, 24)
        self.score_font = pygame.font.SysFont(None, 48)

        # Prepare initial score images
        self.prep_score()
        self.prep_hearts()

    def prep_score(self) -> None:
        """Turn the score into an image that can be displayed."""
        text_str = "SCORE"
        score_str = f"{self.stats.score:,}"

        # Score images that will be rendered
        self.score_text = self.text_font.render(text_str, True, self.text_color)
        self.score_number = self.score_font.render(score_str, True, self.text_color)

        # Display the score at the top-right side of the screen
        self.score_text_rect = self.score_text.get_rect()
        self.score_text_rect.topright = (
            self.screen_rect.right - self.screen_padding,
            self.screen_padding,
        )
        self.score_number_rect = self.score_number.get_rect()
        self.score_number_rect.topright = self.score_text_rect.bottomright

    def prep_hearts(self) -> None:
        """Show how many lives are left."""
        # Text image that will be rendered above the hearts
        lives_str = "LIVES"
        self.lives_text = self.text_font.render(lives_str, True, self.text_color)

        # Display the text at the top-left corner of the screen
        self.lives_text_rect = self.lives_text.get_rect()
        self.lives_text_rect.topleft = (self.screen_padding, self.screen_padding)

        # Creates the heart that represent the player's lives
        self.hearts = Group()
        heart_padding = 0
        for live_number in range(self.stats.lives_left):
            heart = Heart()
            # Position each heart just below the text
            x_pos = self.screen_padding + heart_padding + live_number * heart.rect.width
            y_pos = self.lives_text_rect.bottom
            heart.set_position(x_pos, y_pos)
            self.hearts.add(heart)
            heart_padding += 3  # Adds a small padding between each heart

    def draw_score(self) -> None:
        """Draw score and lives left to the screen."""
        self.screen.blit(self.score_text, self.score_text_rect)
        self.screen.blit(self.score_number, self.score_number_rect)
        self.screen.blit(self.lives_text, self.lives_text_rect)
        self.hearts.draw(self.screen)


class Block(Sprite):
    """A class to define each block that makes the level."""

    def __init__(
        self,
        settings: Settings,
        color: Color = None,
        pattern: bool = True,
    ):
        """Initializes a block of a fixed size."""
        super().__init__()

        self.settings = settings

        if not color:
            self.color = self.settings.BLOCK_COLOR
        else:
            self.color = color

        self.size = self.settings.BLOCK_SIZE
        self.image = Surface((self.size, self.size))
        self.rect = self.image.get_rect()

        if pattern:
            self._draw_pattern()
        else:
            self.image.fill(self.color)

    def set_bottomleft(self, coordinate: Vector2) -> None:
        """Updates the bottomleft position of the block."""
        self.rect.bottomleft = coordinate

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


class Enemy(Sprite):
    """A class to create and control an enemy."""

    def __init__(self, settings: Settings):
        """Initializes the enemy image and rect."""
        super().__init__()

        self.settings = settings
        self.image = pygame.image.load(r"assets\monster.png").convert_alpha()
        self.rect = self.image.get_rect()

        # Used for collision detection with the player
        self.mask = pygame.mask.from_surface(self.image)

        # Set the current direction of the enemy
        self.change_x = self.settings.enemy_speed

    def update(self, platform_limits: Group):
        """Updates the position of the enemy."""
        # Moves the enemy right or left on the platform
        self.rect.x += self.change_x

        # Check for collisions with any platform limit
        limit_hits = pygame.sprite.spritecollideany(self, platform_limits)
        if limit_hits is not None:
            self.image = pygame.transform.flip(self.image, True, False)
            self.change_x *= -1  # Change direction of movement

    def set_bottomleft(self, coordinate: Vector2) -> None:
        """Set the bottomleft position of the enemy on the screen."""
        self.rect.bottomleft = coordinate


class Heart(Sprite):
    """Class to create the shape of a heart to represent the player's lives."""

    def __init__(self):
        """Initializes the heart shape, and puts it inside an image."""
        super().__init__()

        self._shape = [
            "__#####__#####__",
            "_##RRR####RRD##_",
            "##RRRRR##RRRRD##",
            "#RWWRRRRRRRRRDD#",
            "#RWRRRRRRRRRRDD#",
            "#RRRRRRRRRRRRDD#",
            "#RWRRRRRRRRRRDD#",
            "##RRRRRRRRRRDD##",
            "_#RRRRRRRRRRDD#_",
            "_##RRRRRRRRDD##_",
            "__##RRRRRRDD##__",
            "___##RRRRDD##___",
            "____##RRDD##____",
            "_____##DD##_____",
            "______####______",
            "_______##_______",
        ]
        self._C_ALPHA = 175
        self._C_RED = Color(255, 0, 0, self._C_ALPHA)
        self._C_DARK_RED = Color(175, 0, 0, self._C_ALPHA)
        self._C_BLACK = Color(0, 0, 0, self._C_ALPHA)
        self._C_WHITE = Color(255, 255, 255, self._C_ALPHA)
        self._pixel_size = 2
        self._size = self._pixel_size * len(self._shape)

        self.image = Surface((self._size, self._size), flags=pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self._draw_shape()

    def _draw_shape(self) -> None:
        """Helper funtion to create the heart shape inside the image surface
        by drawing rectangles.

        Uses the patter found in self._shape to draw the figure:
            '#': Black rectangle
            'R': Red rectangle
            'D': Darker red rectangle
            'W': White rectangle
        Any other character is ignored, but contributes to padding.
        """
        current_x = self.rect.left
        current_y = self.rect.top

        # Each row in the pattern
        for row in self._shape:
            # Each character in the pattern
            for char in row:
                current_rect = pygame.Rect(
                    current_x, current_y, self._pixel_size, self._pixel_size
                )
                if char == "#":
                    pygame.draw.rect(self.image, self._C_BLACK, current_rect)
                elif char == "R":
                    pygame.draw.rect(self.image, self._C_RED, current_rect)
                elif char == "D":
                    pygame.draw.rect(self.image, self._C_DARK_RED, current_rect)
                elif char == "W":
                    pygame.draw.rect(self.image, self._C_WHITE, current_rect)
                current_x += self._pixel_size

            current_x = self.rect.left
            current_y += self._pixel_size

    def set_position(self, x: int, y: int) -> None:
        """Update the position of the heart relative to the screen."""
        self.rect.x = x
        self.rect.y = y


class Coin(Sprite):
    """Class to create a coin sprite on the level."""

    def __init__(self):
        """Initialize the coin image and position on the screen."""
        super().__init__()

        self.image = pygame.image.load(r"assets\coin.png").convert_alpha()
        self.rect = self.image.get_rect()

    def set_center(self, coordinate: Vector2) -> None:
        """Position the center of the coin at the given coordinate."""
        self.rect.center = coordinate


class Level:
    """A generic super-class used to define a level."""

    def __init__(self, screen: Surface, settings: Settings):
        """Initializes all sprite groups of the level."""
        self.screen = screen
        self.settings = settings

        # Groups to keep track of the level's sprites
        self.platforms = Group()
        self.coins = Group()
        self.enemies = Group()
        self.platform_limits = Group()

        # Keeps track of the starting position of the player
        self.player_start_pos = Vector2(0, 0)

        # Keeps track of how much has this level been
        # shifted left or right
        self.level_shift = 0

    def update(self) -> None:
        """Update everything in this level."""
        self.platforms.update()
        self.platform_limits.update()
        self.coins.update()
        self.enemies.update(self.platform_limits)

    def draw(self) -> None:
        """Draw everything on this level."""

        # Draw the background
        self.screen.fill(self.settings.BG_COLOR)

        # Draw all the sprites that we have
        self.platforms.draw(self.screen)
        self.platform_limits.draw(self.screen)
        self.coins.draw(self.screen)
        self.enemies.draw(self.screen)

    def _create(self, pattern: list[str], level_size: int) -> None:
        """Creates the structure of the level based on a string pattern."""
        current_pos = Vector2(0, self.settings.SCREEN_HEIGHT)

        # Add the platforms starting from the bottom-left of the screen
        for row in pattern[::-1]:
            for object_type in row:
                if object_type == "X":
                    self._create_platform(current_pos)
                elif object_type == "E":
                    self._create_enemy(current_pos)
                    self._create_coin(current_pos)
                elif object_type == "C":
                    self._create_coin(current_pos)
                elif object_type == "#":
                    self._create_enemy_limit(current_pos)
                elif object_type == "P":
                    self.player_start_pos.x = current_pos.x
                    self.player_start_pos.y = current_pos.y

                current_pos.x += self.settings.BLOCK_SIZE

            current_pos.y -= self.settings.BLOCK_SIZE
            current_pos.x = 0

        # Add the blocks that confine the player to the level
        self._add_level_limits(level_size)

    def _create_platform(self, coordinate: Vector2) -> None:
        """Create a new block and add it to the level's platforms."""
        new_block = Block(self.settings)
        new_block.set_bottomleft(coordinate)
        self.platforms.add(new_block)

    def _create_coin(self, coordinate: Vector2) -> None:
        """Create a new coin sprite and add it to the level's coins."""
        # Get the center of what would've been a block
        offset = self.settings.BLOCK_SIZE // 2
        coord_center = Vector2(coordinate.x + offset, coordinate.y - offset)

        # Create the new coin, set its position and add it to coins
        new_coin = Coin()
        new_coin.set_center(coord_center)
        self.coins.add(new_coin)

    def _create_enemy(self, coordinate: Vector2) -> None:
        """Create a new enemy and add it to the level's enemies."""
        new_enemy = Enemy(self.settings)
        new_enemy.set_bottomleft(coordinate)
        self.enemies.add(new_enemy)

    def _create_enemy_limit(self, coordinate: Vector2) -> None:
        """Create a new transparent block and add it to the level's
        platform_limits.
        """
        new_enemy_limit = Block(self.settings, self.settings.BG_COLOR, False)
        new_enemy_limit.set_bottomleft(coordinate)
        self.platform_limits.add(new_enemy_limit)

    def _add_level_limits(self, level_size: int) -> None:
        """Add blocks to the left and right side to define the level's boundaries."""
        left_padding = self.settings.LEFT_SCREEN_LIMIT
        right_padding = self.settings.RIGHT_SCREEN_LIMIT
        screen_height = self.settings.SCREEN_HEIGHT
        block_size = self.settings.BLOCK_SIZE

        # Add the left padding of blocks to the level
        for current_y in range(screen_height, 0, -block_size):
            for current_x in range(-left_padding, 0, block_size):
                new_block = Block(self.settings)
                new_block.set_bottomleft(Vector2(current_x, current_y))
                self.platforms.add(new_block)

        # Add the right padding of blocks to the level
        for current_y in range(screen_height, 0, -block_size):
            for current_x in range(level_size, level_size + right_padding, block_size):
                new_block = Block(self.settings)
                new_block.set_bottomleft(Vector2(current_x, current_y))
                self.platforms.add(new_block)

    def shift_level(self, shift_x: int) -> None:
        """Shifts the whole level right or left, depending of the player's movement."""
        # Keep track of the shift amount
        self.level_shift += shift_x
        self.player_start_pos.x += shift_x

        # Shift all the level sprites
        for platform in self.platforms:
            platform.rect.x += shift_x

        for coin in self.coins:
            coin.rect.x += shift_x

        for enemy in self.enemies:
            enemy.rect.x += shift_x

        for limit in self.platform_limits:
            limit.rect.x += shift_x


class Level_01(Level):
    """A class that defines the layout of level 1."""

    def __init__(self, screen: Surface, settings: Settings):
        """Creates level 1 of the game."""
        super().__init__(screen, settings)

        # The level layout
        self.level = [
            "__#CCEC#__#CCECC#__XX__",
            "___XXXX____XXXXX",
            "",
            "P",
            "XXXXXXXXXXXXXXXXXXXXXXX",
        ]

        self.level_size = self.settings.BLOCK_SIZE * len(self.level[-1])

        self._create(self.level, self.level_size)


class Player(Sprite):
    """A class to create and control the robot player."""

    def __init__(self, screen: Surface, settings: Settings):
        """Initialize the robot player and its position"""
        super().__init__()
        self.screen = screen
        self.settings = settings

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

    def load_level_platforms(self, platforms: Group) -> None:
        """Load the current level's platforms.

        This is needed so the player can know if its colliding with a
        platform and to react accordingly.
        """
        self.level_platforms = platforms

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

    def set_bottomleft(self, coord: Vector2) -> None:
        """Set the bottomleft position of the player on the screen."""
        self.rect.bottomleft = coord

    def _apply_gravity(self) -> None:
        """Moves the player towards the bottom of the screen."""
        self.change_y += 0.7

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
        platform_hits = pygame.sprite.spritecollide(self, self.level_platforms, False)
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
        platform_hits = pygame.sprite.spritecollide(self, self.level_platforms, False)
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

    def __init__(self):
        """Initialize the game an create all resorces needed."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        # Creates the window and sets the caption
        self.screen = pygame.display.set_mode(
            (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Robot Platfomer")

        # Create an instance to store game statistics and scoreboard
        self.stats = GameStats(self.settings)
        self.scoreboard = Scoreboard(self.screen, self.settings, self.stats)

        # Creates the robot the player can control
        self.player = Player(self.screen, self.settings)

        # Create all the levels
        self.level_list: list[Level] = []
        self.level_list.append(Level_01(self.screen, self.settings))

        # Set the current level
        self.current_level = self.level_list[self.stats.level]

        # The player needs the current level's platforms to check if it's
        # colliding with any of them
        self.player.load_level_platforms(self.current_level.platforms)

        # Set the player position at the start of the game
        self.player.set_bottomleft(self.current_level.player_start_pos)

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
                # If the player collides with the head of an enemy and it's
                # falling down after jumping
                if point_of_collision[1] <= 15 and self.player.change_y > 0:
                    self.player.change_y = -6  # Make a little jump
                    self.stats.score += self.settings.ENEMY_POINTS
                    self.scoreboard.prep_score()
                    enemy_hit.kill()
                # The player collided with any other part of the enemy
                else:
                    pygame.time.wait(500)
                    if self.stats.lives_left > 0:
                        self.stats.lives_left -= 1
                        self.scoreboard.prep_hearts()
                        self.player.set_bottomleft(self.current_level.player_start_pos)

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
        self.scoreboard.draw_score()
        pygame.display.flip()


if __name__ == "__main__":
    # Make an instance of the game and run it
    platformer = Platformer()
    platformer.run_game()
