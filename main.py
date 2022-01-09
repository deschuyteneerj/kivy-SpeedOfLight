import random

from kivy import platform
from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.graphics import Color, Line, Quad
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window


class MainWidget(Widget):
    from transforms import transform, transform_2d, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_up, on_touch_down
    # Vanishing point
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    # Vertical lines
    V_NB_LINES = 8
    V_LINES_SPACING = .2  # screen width percentage
    vertical_lines = []

    # Horizontal lines
    H_NB_LINES = 8
    H_LINES_SPACING = .15  # screen height percentage
    horizontal_lines = []

    # Moving effect on horizontal lines
    SPEED = 5
    current_offset_y = 0
    current_y_loop = 0

    # Moving effect on vertical lines
    SPEED_X = 12
    current_speed_x = 0
    current_offset_x = 0

    # Tiles
    NB_TILES = 8
    tiles = []
    tiles_coordinates = []

    # Function to initialize the game
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print(' INIT W:' + str(self.width) + ' H:' + str(self.height))
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
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

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        # Delete coordinates when the tile is off screen
        # ti_y < self.current_y_loop
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
        # print('dt: ' + str(dt * 60))
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        # Activate the movement effect
        self.current_offset_y += self.SPEED * time_factor
        spacing_y = self.H_LINES_SPACING * self.height
        # Loop for infinite moving effect
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
            self.current_y_loop += 1
            self.generate_tiles_coordinates()
        # Activate the controls on keyboard/touch
        self.current_offset_x += self.current_speed_x * time_factor


class SpeedOfLightApp(App):
    pass


SpeedOfLightApp().run()
