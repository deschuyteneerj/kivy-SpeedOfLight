# Functions to control the spaceship
def keyboard_closed(self):
    self.keyboard.unbind(on_key_down=self.on_keyboard_down)
    self.keyboard.bind(on_key_up=self.on_keyboard_up)
    self.keyboard = None


def on_touch_down(self, touch):
    if touch.x < self.width / 2:
        self.current_speed_x = self.SPEED_X
    else:
        self.current_speed_x = -self.SPEED_X


def on_touch_up(self, touch):
    self.current_speed_x = 0


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.current_speed_x = self.SPEED_X
    elif keycode[1] == 'right':
        self.current_speed_x = -self.SPEED_X
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0