from kivy.app import App
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget


class MainWidget(Widget):
    # Vanishing point
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    # Vertical lines
    V_NB_LINES = 10
    V_LINES_SPACING = .25  # screen width percentage
    vertical_lines = []

    # Horizontal lines
    H_NB_LINES = 15
    H_LINES_SPACING = .1  # screen height percentage
    horizontal_lines = []

    # Moving effect on horizontal lines
    SPEED = 4
    current_offset_y = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print(' INIT W:' + str(self.width) + ' H:' + str(self.height))
        self.init_vertical_lines()
        self.init_horizontal_lines()
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_parent(self, widget, parent):
        print('ON PARENT W:' + str(self.width) + ' H:' + str(self.height))

    def on_size(self, *args):
        pass
        # self.update_vertical_lines()
        # self.update_horizontal_lines()
        # print('ON SIZE W:' + str(self.width) + ' H:' + str(self.height))
        # self.perspective_point_x = self.width / 2
        # self.perspective_point_y = self.height * 0.75

    def on_perspective_point_x(self, widget, value):
        # print('PX: ' + str(value))
        pass

    def on_perspective_point_y(self, widget, value):
        # print('PY: ' + str(value))
        pass

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        central_line_x = self.width / 2
        spacing = self.V_LINES_SPACING * self.width
        offset = -int(self.V_NB_LINES / 2) + 0.5
        for i in range(0, self.V_NB_LINES):
            line_x = int(central_line_x + offset * spacing)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]
            offset += 1

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        central_line_x = self.width / 2
        spacing = self.V_LINES_SPACING * self.width
        offset = -int(self.V_NB_LINES / 2) + 0.5

        xmin = central_line_x + offset * spacing
        xmax = central_line_x - offset * spacing
        spacing_y = self.H_LINES_SPACING * self.height
        for i in range(0, self.H_NB_LINES):
            line_y = i * spacing_y - self.current_offset_y
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    # Function to change perspective from 2D to vanishing point perspective
    def transform(self, x, y):
        # return self.transform_2d(x, y)
        return self.transform_perspective(x, y)

    def transform_2d(self, x, y):
        return int(x), int(y)

    def transform_perspective(self, x, y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y

        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = diff_y / self.perspective_point_y
        factor_y = pow(factor_y, 4)

        offset_x = diff_x * factor_y

        tr_x = self.perspective_point_x + offset_x
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
        return int(tr_x), int(tr_y)

    # Function refresh 60 fps
    def update(self, dt):
        # print('update')
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.current_offset_y += self.SPEED

        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y


class SpeedOfLightApp(App):
    pass


SpeedOfLightApp().run()
