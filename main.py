import arcade

WIDTH = 800
HEIGHT = 600

PLAYER_MOVEMENT_SPEED = 3


class Entity:
    def __init__(self, posX=0, posY=0, width=1, height=1, color=arcade.color.RED):
        self.x = posX
        self.y = posY
        self.width = width
        self.height = height
        self.color = color
        self.sprite = None

    def draw(self):
        arcade.draw_rectangle_filled(
            self.x,
            self.y,
            self.width,
            self.height,
            self.color
        )


class Player(Entity):

    def __init__(self, posX, posY, width, height, color=arcade.color.RED):
        super().__init__(posX, posY, width, height, color)
        self.moveX = 0
        self.moveY = 0


class Game(arcade.Window):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)
        arcade.set_background_color(arcade.color.BLUE)

        self.person = Player(500, 500, 50, 100)

    def setup(self):
        self.person.sprite = arcade.Sprite("sprites/man.png", scale=0.06)
        self.person.sprite.center_x = self.person.x
        self.person.sprite.center_y = self.person.y

    def on_draw(self):
        arcade.start_render()

        self.person.sprite.draw()

    def on_update(self, delta_time: float):
        self.person.sprite.center_x += self.person.moveX
        self.person.sprite.center_y += self.person.moveY

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.person.moveX = -PLAYER_MOVEMENT_SPEED #x-axis
        if symbol == arcade.key.D:
            self.person.moveX = PLAYER_MOVEMENT_SPEED #x-axis
        if symbol == arcade.key.W:
            self.person.moveY = PLAYER_MOVEMENT_SPEED #y-axis
        if symbol == arcade.key.S:
            self.person.moveY = -PLAYER_MOVEMENT_SPEED #y-axis

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A or symbol == arcade.key.D: #x-axis
            self.person.moveX = 0
        if symbol == arcade.key.W or symbol == arcade.key.S: #y-axis
            self.person.moveY = 0


def main():
    window = Game(WIDTH, HEIGHT, 'RmPG')
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()

'''
to-do list

classes: entity - person - enemy, room - map, scene (или camera)
connect sprites
UI
menu

'''
