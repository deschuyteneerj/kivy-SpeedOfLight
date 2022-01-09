import random

from kivy import platform
from kivy.config import Config

Config.set('graphics', 'width', '960')
Config.set('graphics', 'height', '540')

from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.lang import Builder

Builder.load_file('menu.kv')


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2d, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_up, on_touch_down

    # Menu
    menu_widget = ObjectProperty()

    # Vanishing point
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    # Vertical lines
    V_NB_LINES = 8
    V_LINES_SPACING = .1  # screen width percentage
    vertical_lines = []

    # Horizontal lines
    H_NB_LINES = 8
    H_LINES_SPACING = .15  # screen height percentage
    horizontal_lines = []

    # Moving effect on horizontal lines
    SPEED = .8
    current_offset_y = 0
    current_y_loop = 0

    # Moving effect on vertical lines
    SPEED_X = 3
    current_speed_x = 0
    current_offset_x = 0

    # Tiles
    NB_TILES = 8
    tiles = []
    tiles_coordinates = []

    # Spaceship
    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    # Game status
    state_game_over = False
    state_game_has_started = False

    # Function to initialize the game
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()

        if self.is_desktop():
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.on_keyboard_down)
            self.keyboard.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    # Function to check if on computer for keyboards controls
    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    # Functions x and y to get coordinates from the screen
    def get_line_x_from_index(self, index):
        # Vertical centered line on screen
        central_line_x = self.perspective_point_x
        # Spacing between two lines
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    # Generate 10 tiles forward for the beginning of the game
    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    # Generate tiles for the game
    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        # Delete coordinates when the tile is off screen
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]
        # Modify the coordinates of tiles with moving effect
        if len(self.tiles_coordinates) > 0:
            last_coordinate = self.tiles_coordinates[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1] + 1
        # Append a new tile
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            # Random generation of tiles
            # 0 = forward
            # 1 = right
            # 2 = left
            r = random.randint(0, 2)
            # First vertical line on the left
            start_index = -int(self.V_NB_LINES / 2) + 1
            # Last vertical line on the right
            end_index = start_index + self.V_NB_LINES - 1
            # Stay on the grid at all cost! (Go left if max on the right, go right if max on the left)
            if last_x <= start_index:
                r = 1
            if last_x + 1 >= end_index:
                r = 2
            self.tiles_coordinates.append((last_x, last_y))
            # Turn to the right
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            # Turn to the left
            elif r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y += 1

    # Every Init and Update functions
    # Ship
    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()
            # Triangles() coordinates in order
            #     2
            #  1     3

    def update_ship(self):
        # Measurements in proportion to the screen size
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height
        self.ship_coordinates[0] = (center_x - half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + half_width, base_y)
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    # Function to check if ship is always on the road grid
    def check_ship_collisions(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            # Check if we are on the 2 lasts tiles, no need to test collisions after 2nd tile
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    # Function to check collisions
    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    # Tiles
    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)
            # Quad() coordinates in order
            # 2     3
            #
            # 1     4
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    # Vertical lines
    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        # First vertical line on the left
        start_index = -int(self.V_NB_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    # Horizontal lines
    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        # First vertical line on the left
        start_index = -int(self.V_NB_LINES / 2) + 1
        # Last vertical line on the right
        end_index = start_index + self.V_NB_LINES - 1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    # Function refresh 60 fps
    def update(self, dt):
        # print('dt: ' + str(dt*60))
        time_factor = dt * 60

        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED * self.height / 100
            # Activate the movement effect
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            # Loop for infinite moving effect
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.generate_tiles_coordinates()

            # Activate the controls on keyboard/touch
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        # Check game over
        if not self.check_ship_collisions() and not self.state_game_over:
            self.state_game_over = True
            self.menu_widget.opacity = 1
            print('Game Over')

    def on_menu_button_pressed(self):
        self.state_game_has_started = True
        self.menu_widget.opacity = 0


class SpeedOfLightApp(App):
    pass


SpeedOfLightApp().run()
