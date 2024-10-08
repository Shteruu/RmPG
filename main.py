import arcade

WIDTH = 800
HEIGHT = 600


class Entity:
    def __init__(self, posX=0, posY=0, width=1, height=1, color=arcade.color.RED):
        self.x = posX
        self.y = posY
        self.width = width
        self.height = height
        self.color = color

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

        self.person = Player(100, 100, 50, 100)

    def on_draw(self):
        arcade.start_render()

        self.person.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.person.y += 100

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.person.y -= 100


if __name__ == '__main__':
    window = Game(WIDTH, HEIGHT, 'RmPG')

    arcade.run()

'''
to-do list

classes: entity - person - enemy, room - map
connect sprites

'''

