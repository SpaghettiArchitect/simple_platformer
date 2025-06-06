import sys

import pygame
from pygame import Color, Surface, Vector2
from pygame.sprite import Group, GroupSingle, Sprite


class Settings:
    """A class to manage the game settings."""

    def __init__(self):
        """Initialize the game settings."""
        # Screen settings
        self.SCREEN_WIDTH = 850
        self.SCREEN_HEIGHT = 500
        self.FPS = 60
        self.BG_COLOR = Color(18, 148, 199)
        self.GAME_TITLE = "Robot Platformer"

        # Player's settings
        self.player_speed = 5
        self.PLAYER_LIVES = 5

        # Block's settings
        self.BLOCK_SIZE = 50
        self.BLOCK_COLOR = Color(88, 115, 22)

        # Enemies' settings
        self.enemy_speed = 3
        self.ENEMY_POINTS = 200

        # Coin's settings
        self.COIN_POINTS = 100

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


class Button(Sprite):
    """Class to create a new button."""

    def __init__(
        self,
        text: str,
        text_size: int = 48,
        text_color: Color = Color(0, 0, 0),
        bg_color: Color = Color(255, 255, 255),
        padding: Vector2 = Vector2(20, 20),
    ):
        """Initilizes a new button.

        - text: the string text inside the button.
        - text_size (optional): the size to render the text.
        - text_color (optional): the color to render the text.
        - bg_color (optional): the color to fill the button with.
        - padding (optional): the total left and top padding that would be
        added to the button size.
        """
        super().__init__()

        # Initialize the font to use
        self._font = pygame.font.SysFont(None, text_size)

        # Initialize the text image and its rect
        self._txt_image = self._font.render(text, True, text_color)
        self._txt_rect = self._txt_image.get_rect()

        # Calculate the button's width and height based on the padding
        self._button_width = self._txt_rect.width + padding.x
        self._button_height = self._txt_rect.height + padding.y

        # Initialize the buttom surface and its rect
        self.image = Surface((self._button_width, self._button_height))
        self.image.fill(bg_color)
        self.rect = self.image.get_rect()

        # Puts the text image at the center of the button
        self._txt_rect.center = self.rect.center
        self.image.blit(self._txt_image, self._txt_rect)


class Block(Sprite):
    """A class to define each block that makes the level."""

    def __init__(
        self,
        settings: Settings,
        color: Color,
        pattern: bool = True,
    ):
        """Initializes a block of a fixed size."""
        super().__init__()

        self.settings = settings

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
        """Draws a triangular pattern inside the block, so it will look
        less two dimensional.
        """
        # Top triangle
        top_points = (self.rect.topleft, self.rect.topright, self.rect.center)
        self._draw_triangle(top_points, 0.7)

        # Right triangle
        right_points = (self.rect.topright, self.rect.bottomright, self.rect.center)
        self._draw_triangle(right_points, 0.9)

        # Bottom triangle
        bottom_points = (self.rect.bottomleft, self.rect.bottomright, self.rect.center)
        self._draw_triangle(bottom_points)

        # Left triangle
        left_points = (self.rect.bottomleft, self.rect.topleft, self.rect.center)
        self._draw_triangle(left_points, 0.8)

        # Draw lines for better contrast
        self._draw_lines()

    def _draw_triangle(self, points: tuple[int], gamma: float = 1) -> None:
        """Draw a triangular shape inside the block. The color to fill the
        shape with is taken from self.color.

        - points: the cordinates that make the vertices of the shape.
        - gamma (optional): controls the brightness of the color.
        """
        # Check if exactly three coordinates where provided
        if len(points) != 3:
            raise ValueError(
                f"The triangle needs to have exactly 3 points, you provided {len(points)}"
            )
        # Draws the triangular shape
        pygame.draw.polygon(self.image, self.color.correct_gamma(gamma), points)

    def _draw_lines(self, color: Color = None) -> None:
        """Draw two diagonal lines inside the block, and another two lines
        on the left and top sides of the block.

        - color (optional): the color of the lines. If no color is provided
        the one in self.color will be used.
        """
        # Check for color
        if color is None:
            color = self.color

        # Diagonal lines
        pygame.draw.line(
            self.image,
            color,
            self.rect.topleft,
            self.rect.bottomright,
        )
        pygame.draw.line(
            self.image,
            color,
            self.rect.bottomleft,
            self.rect.topright,
        )

        # Top side and left side lines
        pygame.draw.line(
            self.image,
            color,
            self.rect.topleft,
            self.rect.topright,
        )
        pygame.draw.line(
            self.image,
            color,
            self.rect.topleft,
            self.rect.bottomleft,
        )


class Enemy(Sprite):
    """A class to create and control an enemy."""

    def __init__(self, settings: Settings):
        """Initializes the enemy object with all required attributes."""
        super().__init__()

        self.settings = settings
        self.image = pygame.image.load(r"assets\monster.png").convert_alpha()
        self.rect = self.image.get_rect()

        # Used for collision detection with the player
        self.mask = pygame.mask.from_surface(self.image)

        # Every value below this limit will be consider to be the top
        # of the enemy image
        self.top_limit = 15

        # Set the current speed and direction of movement
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
        self._C_ALPHA = 200
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

        # Make the image a little bit smaller and get the rect
        self.image = pygame.transform.smoothscale(self.image, (30, 30))
        self.rect = self.image.get_rect()

        # Changes the color of the coin to a darker yellow
        new_yellow = Color(252, 174, 4, 255)
        self.image.fill(new_yellow, special_flags=pygame.BLEND_RGBA_MIN)

        # The mask is used to calculate collisions
        self.mask = pygame.mask.from_surface(self.image)

    def set_center(self, coordinate: Vector2) -> None:
        """Position the center of the coin at the given coordinate."""
        self.rect.center = coordinate


class Door(Sprite):
    """A class to create a door for the level."""

    def __init__(self):
        """Initialize the door object with all required attributes."""
        super().__init__()

        self.image = pygame.image.load(r"assets\door.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def set_bottomleft(self, coordinate: Vector2) -> None:
        """Set the bottomleft position of the door relative to the screen."""
        self.rect.bottomleft = coordinate


class Level:
    """A generic super-class used to define a level."""

    def __init__(self, screen: Surface, settings: Settings):
        """Initializes all sprite groups of the level."""
        self.screen = screen
        self.settings = settings

        # This colors can be ovewritten on each child level
        self.bg_color = self.settings.BG_COLOR
        self.block_color = self.settings.BLOCK_COLOR

        # Groups to keep track of the level's sprites
        self.platforms = Group()
        self.coins = Group()
        self.enemies = Group()
        self.platform_limits = Group()
        self.door = GroupSingle()

        # Keeps track of the starting position of the player
        self.player_start_pos = Vector2(0, 0)

        # Keeps track of how much has this level been
        # shifted left or right
        self.level_shift = 0

    def update(self) -> None:
        """Update everything in this level."""
        self.platforms.update()
        self.platform_limits.update()
        self.door.update()
        self.coins.update()
        self.enemies.update(self.platform_limits)

    def draw(self) -> None:
        """Draw everything on this level."""
        # Draw the background
        self.screen.fill(self.bg_color)

        # Draw all the sprites that we have
        self.platforms.draw(self.screen)
        self.platform_limits.draw(self.screen)
        self.door.draw(self.screen)
        self.coins.draw(self.screen)
        self.enemies.draw(self.screen)

    def _create(self, pattern: list[str]) -> None:
        """Creates the structure of the level based on a string pattern.

        - pattern: a list of strings, where each character represents an
        object that will be added to the level.
            - 'X': a Block object (with a pattern inside).
            - 'E': an Enemy object.
            - 'C': a Coin object.
            - '#': a special kind of Block, used to change the direction
            of enemies when both of them collide.
            - 'P': sets the player position at the start of the level.
            - 'D': a Door object, used to end the level.

        Any other character is ignored, but adds padding between objects.
        """
        # Calculate the level size based on the total number of characters
        # in the last row of the pattern
        self.level_size = len(pattern[-1]) * self.settings.BLOCK_SIZE

        # Add the platforms starting from the bottom-left of the screen
        current_pos = Vector2(0, self.settings.SCREEN_HEIGHT)
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
                    self._create_platform_limit(current_pos)
                elif object_type == "P":
                    self.player_start_pos.x = current_pos.x
                    self.player_start_pos.y = current_pos.y
                elif object_type == "D":
                    self._create_door(current_pos)

                current_pos.x += self.settings.BLOCK_SIZE

            current_pos.y -= self.settings.BLOCK_SIZE
            current_pos.x = 0

        # Add the blocks that confine the player to the level
        self._add_level_limits(self.level_size)

    def _create_platform(self, coordinate: Vector2) -> None:
        """Create a new block and add it to the level's platforms.

        - coordinate: the position of the platform on the level.
        """
        new_block = Block(self.settings, self.block_color)
        new_block.set_bottomleft(coordinate)
        self.platforms.add(new_block)

    def _create_coin(self, coordinate: Vector2) -> None:
        """Create a new coin sprite and add it to the level's coins.

        - coordinate: the position of the coin on the level.
        """
        # Get the center of what would've been a block
        offset = self.settings.BLOCK_SIZE // 2
        coord_center = Vector2(coordinate.x + offset, coordinate.y - offset)

        # Create the new coin, set its position and add it to coins
        new_coin = Coin()
        new_coin.set_center(coord_center)
        self.coins.add(new_coin)

    def _create_enemy(self, coordinate: Vector2) -> None:
        """Create a new enemy and add it to the level's enemies.

        - coordinate: the position of the enemy on the level.
        """
        new_enemy = Enemy(self.settings)
        new_enemy.set_bottomleft(coordinate)
        self.enemies.add(new_enemy)

    def _create_platform_limit(self, coordinate: Vector2) -> None:
        """Create a new transparent block and add it to the level's
        platform_limits.

        - coordinate: the postion of the block limit on the level.
        """
        new_enemy_limit = Block(self.settings, self.bg_color, False)
        new_enemy_limit.set_bottomleft(coordinate)
        self.platform_limits.add(new_enemy_limit)

    def _create_door(self, coordinate: Vector2) -> None:
        """Create a new door and add it to the door's group. There should be
        only one door peer level.

        - coordinate: the position of the door on the level.
        """
        new_door = Door()
        new_door.set_bottomleft(coordinate)
        self.door.add(new_door)

    def _add_level_limits(self, level_size: int) -> None:
        """Add blocks to the left and right side to define the level's boundaries.

        - level_size: the total width of the level.
        """
        left_padding = self.settings.LEFT_SCREEN_LIMIT
        right_padding = self.settings.RIGHT_SCREEN_LIMIT
        screen_height = self.settings.SCREEN_HEIGHT
        block_size = self.settings.BLOCK_SIZE

        # Add the left padding of blocks to the level
        for current_y in range(screen_height, 0, -block_size):
            for current_x in range(-left_padding, 0, block_size):
                new_block = Block(self.settings, self.block_color)
                new_block.set_bottomleft(Vector2(current_x, current_y))
                self.platforms.add(new_block)

        # Add the right padding of blocks to the level
        for current_y in range(screen_height, 0, -block_size):
            for current_x in range(level_size, level_size + right_padding, block_size):
                new_block = Block(self.settings, self.block_color)
                new_block.set_bottomleft(Vector2(current_x, current_y))
                self.platforms.add(new_block)

    def shift_level(self, shift_x: int) -> None:
        """Shifts the whole level right or left, depending of the player's movement.

        - shift_x: the total amount to shift the level relative to the screen.
        If positive, shifts the level to the right. If negative, shift the level
        to the left.
        """
        # Keep track of the shift amount
        self.level_shift += shift_x

        # Move the player's starter position
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

        # Move the door's position
        self.door.sprite.rect.x += shift_x


class MainMenu(Level):
    """Class to create a menu screen when starting the game."""

    def __init__(self, screen: Surface, settings: Settings):
        """Initialize the menu as if it was a another level.

        - screen: surface were the level will be drawn.
        - settings: the current game's settings instance.
        """
        super().__init__(screen, settings)

        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.settings = settings

        # This colors will be needed to create buttons and text
        self.bg_color = Color(30, 30, 30)
        self.text_color = Color(255, 255, 255)

        # The pattern for this level
        self.level_pattern = [
            "X_______________X",
            "XX______P______XX",
            "XXXXXXXXXXXXXXXXX",
        ]

        # Create the current level
        self._create(self.level_pattern)

        # Create the title for the game and the button to start it
        self._create_title()
        self._create_title_hearts()
        self._create_button()

    def _create_title(self) -> None:
        """Add the title for the game on the current screen."""
        self.font = pygame.font.SysFont(None, 52)
        # Title image that will be rendered
        self.title_image = self.font.render(
            self.settings.GAME_TITLE.upper(),
            True,
            self.text_color,
        )
        self.title_image_rect = self.title_image.get_rect()

        # Position the image in the screen
        self.title_image_rect.midtop = (self.screen_rect.centerx, 100)

    def _create_title_hearts(self) -> None:
        """Add two hearts as decorations at the left and right side of the
        title.
        """
        self.heart_left = Heart()
        self.heart_left.rect.midright = self.title_image_rect.midleft

        self.heart_right = Heart()
        self.heart_right.rect.midleft = self.title_image_rect.midright

    def _create_button(self) -> None:
        """Create the start game button and set its position."""
        self.start_btn = Button(
            "START GAME",
            32,
            self.text_color,
            self.settings.BLOCK_COLOR,
        )
        self.start_btn.rect.center = self.screen_rect.center
        self.platforms.add(self.start_btn)

    def draw(self) -> None:
        """Draw all images and sprites of the Menu to the screen."""
        super().draw()
        self.screen.blit(self.title_image, self.title_image_rect)
        self.screen.blit(self.heart_right.image, self.heart_right.rect)
        self.screen.blit(self.heart_left.image, self.heart_left.rect)


class Level_01(Level):
    """A class that defines the layout of level 1."""

    def __init__(self, screen: Surface, settings: Settings):
        """Creates level 1 of the game."""
        super().__init__(screen, settings)

        # The level layout
        self.level_pattern = [
            "___________________________D____",
            "CCCC_____CC________C_______X____",
            "XXX_C___C__C______C#ECCC#_______",
            "____C__C____C____C__XXXXC_______",
            "___#CCEC#__#CCECC#_____XXC_#ECC#",
            "____XXXX____XXXXXC______XXC_XXX_",
            "_________________C________C_____",
            "_P_CCCC_____#CCCEC#__#ECCCCC#___",
            "XXXXXXX______XXXXX____XXXXXX____",
        ]

        # Create the level
        self._create(self.level_pattern)


class Level_02(Level):
    def __init__(self, screen: Surface, settings: Settings):
        """Creates level 1 of the game."""
        super().__init__(screen, settings)

        self.bg_color = Color(163, 147, 191)
        self.block_color = Color(97, 63, 117)

        # The level layout
        self.level_pattern = [
            "_#CCCCE#_P#CCCCE##CCE##CCCE##CCCCCE##CCCCE##CCECCC#",
            "__XXXXX__XXXXXXX__XXX__XXXX__XXXXXX__XXXXX__XXXXXXX",
            "___________________________________________________",
            "#CCE##CCCE#__#CCCCE#___#CCCE##CCCCCE#___#CCCCE#___D",
            "_XXX__XXXX____XXXXX_____XXXX__XXXXXX_____XXXXX___CC",
            "_________________________________________________XX",
            "#CCCE##CCCE#__#CCCCE#_#CCCE#__#CCCCCE#____#CCCE#___",
            "_XXXX__XXXX____XXXXX___XXXX____XXXXXX______XXXX____",
        ]

        # Create the level
        self._create(self.level_pattern)


class GameOver:
    """Class to create a game over screen."""

    def __init__(self, screen: Surface, stats: GameStats):
        """Initializes the all the elements on the game over screen.

        - screen: the screen surface where game over will be displayed.
        - stats: the current game stats for the game.
        """
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.stats = stats

        self._create_game_over_text()
        self._create_score_text()
        self._create_menu_button()

    def _create_game_over_text(self) -> None:
        """Creates the 'Game Over' image text and sets its position."""
        text_font = pygame.font.SysFont(None, 72)

        # Create the text image and set its position
        self.text_image = text_font.render(
            "GAME OVER",
            True,
            Color(255, 50, 50),
        )
        self.text_image_rect = self.text_image.get_rect()
        self.text_image_rect.center = (self.screen_rect.centerx, 200)

    def _create_score_text(self) -> None:
        """Creates the score text image and sets its position."""
        score_font = pygame.font.SysFont(None, 32)
        score_text = f"Your score: {self.stats.score}"

        # Create the score image
        self.score_image = score_font.render(
            score_text,
            True,
            Color(255, 255, 255),
        )
        self.score_image_rect = self.score_image.get_rect()

        # Set the position of the score below the game over title
        self.score_image_rect.midtop = self.text_image_rect.midbottom
        self.score_image_rect.top += 20

    def _create_menu_button(self):
        """Creates the menu button and sets its position."""
        # Create the button
        self.menu_btn = Button(
            "GO TO MAIN MENU",
            32,
            Color(255, 255, 255),
            Color(88, 115, 22),
        )
        # Set the position of the button just below the score
        self.menu_btn.rect.midtop = self.score_image_rect.midbottom
        self.menu_btn.rect.top += 30

    def draw(self) -> None:
        """Draw the game over screen and set the mouse visible."""
        self.screen.fill(Color(30, 30, 30))
        self.screen.blit(self.text_image, self.text_image_rect)
        self.screen.blit(self.score_image, self.score_image_rect)
        self.screen.blit(self.menu_btn.image, self.menu_btn.rect)
        pygame.mouse.set_visible(True)
        pygame.display.flip()


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

    def bounce(self) -> None:
        """Make the player jump a little after hitting the top of
        an enemy.
        """
        if not self.on_ground:
            self.change_y = -7

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

        # Start game clock and settings
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        # Create the icon of the application
        self.icon = Heart().image
        pygame.display.set_icon(self.icon)

        # Creates the window and sets the caption
        self.screen = pygame.display.set_mode(
            (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
        )
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption(self.settings.GAME_TITLE)

        # Create an instance to store game statistics and scoreboard
        self.stats = GameStats(self.settings)
        self.scoreboard = Scoreboard(self.screen, self.settings, self.stats)

        # Creates the robot the player can control
        self.player = Player(self.screen, self.settings)

        # The list to hold all levels
        self.level_list = []

        # The state of the game
        self.game_active = False
        self.game_over = False

        # The main menu of the game
        self.menu = MainMenu(self.screen, self.settings)

        # This will hold the game over object when the game ends
        self.game_over_screen = None

        # Set the position of the player on the current level. At the start
        # the game starts in the main menu
        self.current_level = self.menu
        self._set_player_on_level()

    def run_game(self) -> None:
        """Starts the main loop of the game."""

        while True:
            self._check_events()
            if not self.game_over:
                self.current_level.update()
                self.player.update()

                if self.game_active:
                    self._update_level_shift()
                    self._check_all_player_collisions()
                self._update_screen()
            else:
                self.game_over_screen.draw()
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

            elif self.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_main_menu_button(mouse_pos)

            elif not self.game_active and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_start_button(mouse_pos)

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

    def _check_start_button(self, mouse_pos: tuple[int, int]) -> None:
        """Check if the start game button on the MainMenu level has been
        pressed. If so, reset all stats, create the levels, load the player
        and set the mouse cursor to invisible.

        - mouse_pos: the current position of the mouse on the screen.
        """
        start_pressed = self.menu.start_btn.rect.collidepoint(mouse_pos)

        if start_pressed:
            self.game_active = True
            self._start_game()

    def _check_main_menu_button(self, mouse_pos: tuple[int, int]) -> None:
        """Check if the button in the game over screen has been pressed.
        If so, load the main menu screen.
        """
        menu_btn_pressed = self.game_over_screen.menu_btn.rect.collidepoint(mouse_pos)

        if menu_btn_pressed:
            self.game_over = False
            self.game_active = False
            self.current_level = self.menu
            self._set_player_on_level()

    def _check_player_screen_collisions(self) -> None:
        """Check if the player is touching the bottom part of the screen."""
        if self.player.rect.bottom >= self.settings.SCREEN_HEIGHT:
            self._player_hit()

    def _check_player_enemy_collisions(self) -> None:
        """Checks if the player has collided with any enemy using masks.

        - If the player is falling down and collides with the top of the
        enemy mask, the enemy is deleted and the player bounces a little.
        - If the player touches any other part of the enemy, the player
        loses a life and their position is restarted to the start of the
        level.
        """
        enemy_hit = pygame.sprite.spritecollideany(
            self.player,
            self.current_level.enemies,
            collided=pygame.sprite.collide_mask,
        )

        if enemy_hit is not None:
            # Get the point of collision
            point_of_collision = pygame.sprite.collide_mask(
                enemy_hit,
                self.player,
            )

            # We compare the y-value of the collision point with the top
            # limit of the enemy hit
            hits_top_of_enemy = point_of_collision[1] <= enemy_hit.top_limit

            # If the player collides with the top of an enemy and they are
            # falling down after jumping
            if hits_top_of_enemy and self.player.change_y > 0:
                self._enemy_hit(enemy_hit)
            # The player collided with any other part of the enemy
            else:
                self._player_hit()

    def _check_player_coin_collisions(self) -> None:
        """Check if the player has collided with any coin. If so, augment
        the game's score.
        """
        coins_hit_list = pygame.sprite.spritecollide(
            self.player,
            self.current_level.coins,
            True,
            collided=pygame.sprite.collide_mask,
        )

        for _ in coins_hit_list:
            self.stats.score += self.settings.COIN_POINTS
            self.scoreboard.prep_score()

    def _check_player_door_collision(self) -> None:
        """Check if the player has collided with the level's door."""
        door_hit = pygame.sprite.spritecollideany(
            self.player,
            self.current_level.door,
            collided=pygame.sprite.collide_mask,
        )
        # If the player collided with the door, load the next level
        if door_hit is not None:
            self._load_next_level()

    def _check_all_player_collisions(self) -> None:
        """Helper funtion to check if the player is colliding with any
        enemy, coin or the bottom of the screen, and react accordingly.
        """
        self._check_player_screen_collisions()
        self._check_player_enemy_collisions()
        self._check_player_coin_collisions()
        self._check_player_door_collision()

    def _enemy_hit(self, enemy: Enemy) -> None:
        """Respond to the enemy being hit from the top by the player."""
        self.player.bounce()  # Make a little jump
        self.stats.score += self.settings.ENEMY_POINTS
        self.scoreboard.prep_score()
        enemy.kill()

    def _player_hit(self) -> None:
        """Respond to the player being hit by an enemy."""
        pygame.time.wait(500)
        if self.stats.lives_left > 1:
            self.stats.lives_left -= 1
            self.scoreboard.prep_hearts()
            self.player.set_bottomleft(self.current_level.player_start_pos)
        else:
            self._show_game_over()

    def _start_game(self) -> None:
        """Starts a new game."""
        # Reset the game statistics
        self.stats.reset_statistics()
        self.scoreboard.prep_score()
        self.scoreboard.prep_hearts()

        # Load levels
        self._load_levels()

        # Set the player's postition on the current level
        self._set_player_on_level()

        # Hide the mouse cursor
        pygame.mouse.set_visible(False)

    def _load_levels(self) -> None:
        """Loads all level and sets the current level."""
        self.level_list.clear()
        self.level_list.append(Level_01(self.screen, self.settings))
        self.level_list.append(Level_02(self.screen, self.settings))
        self.current_level = self.level_list[self.stats.level]

    def _set_player_on_level(self) -> None:
        """Pass the level's platforms to the player and set its position."""
        self.player.load_level_platforms(self.current_level.platforms)
        self.player.set_bottomleft(self.current_level.player_start_pos)

    def _load_next_level(self) -> None:
        """Loads the next level from self.level_list if there is one.
        If there isn't any level left, show the game over screen.
        """
        if self.stats.level + 1 < len(self.level_list):
            self.stats.level += 1
            self.current_level = self.level_list[self.stats.level]
            self._set_player_on_level()
        else:
            self._show_game_over()

    def _show_game_over(self) -> None:
        """End the current game, and show the game over screen."""
        self.game_over = True
        self.game_over_screen = GameOver(self.screen, self.stats)

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
        if self.game_active:
            self.scoreboard.draw_score()
        pygame.display.flip()


if __name__ == "__main__":
    # Make an instance of the game and run it
    platformer = Platformer()
    platformer.run_game()
