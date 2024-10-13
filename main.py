import arcade

WIDTH = 800
HEIGHT = 600

PLAYER_MOVEMENT_SPEED = 3


def load_texture_pair(filename, x=0, y=0):
    """
    Load a texture pair, with the mirror image.
    """
    return [
        arcade.load_texture(file_name=filename,
                            x=x, y=y),

        arcade.load_texture(file_name=filename,
                            flipped_horizontally=True,
                            x=x, y=y),
    ]


def load_crop_texture_pair(filename, image_width, image_height, x=0, y=0):
    """
    Load a cropped texture pair, with the mirror image.
    """
    return [
        arcade.load_texture(file_name=filename,
                            x=x, y=y,
                            width=image_width,
                            height=image_height),

        arcade.load_texture(file_name=filename,
                            flipped_horizontally=True,
                            x=x, y=y,
                            width=image_width,
                            height=image_height),
    ]


class Entity(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.cur_texture = 0

        self.stay_texture_pair = load_crop_texture_pair("sprites/Forward.png", 64, 64)

        self.walk_textures = []
        for i in range(4):
            texture = load_crop_texture_pair("sprites/Forward.png", 64, 64, x=i*64)
            self.walk_textures.append(texture)

        self.sprite = None
        self.texture = self.stay_texture_pair[0]

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.stay_texture_pair[0]
            return

        self.cur_texture += 1
        if self.cur_texture > 3:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][0]


class Player(Entity):

    def __init__(self):
        super().__init__()


class Game(arcade.Window):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)
        arcade.set_background_color(arcade.color.BLUE)

        self.scene = None

        self.physics_engine = None

        self.person = None

        self.map = None

    def setup(self):
        self.scene = arcade.Scene()

        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Map")

        #self.person.sprite = arcade.Sprite("sprites/Forward.png", image_width=64, image_height=64)
        #load_texture_pair("sprites/Forward.png")

        self.person = Player()
        self.person.center_x = 500
        self.person.center_y = 400
        self.scene.add_sprite("Player", self.person)

        self.scene.add_sprite_list("sprites/Forward.png")

    def on_draw(self):
        arcade.start_render()

        self.scene.draw()

    def on_update(self, delta_time: float):
        self.person.center_x += self.person.change_x
        self.person.center_y += self.person.change_y

        self.person.update_animation(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.person.change_x += -PLAYER_MOVEMENT_SPEED #x-axis
        if symbol == arcade.key.D:
            self.person.change_x += PLAYER_MOVEMENT_SPEED #x-axis
        if symbol == arcade.key.W:
            self.person.change_y += PLAYER_MOVEMENT_SPEED #y-axis
        if symbol == arcade.key.S:
            self.person.change_y += -PLAYER_MOVEMENT_SPEED #y-axis

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.person.change_x += PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.D:
            self.person.change_x += -PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.W:
            self.person.change_y += -PLAYER_MOVEMENT_SPEED  # y-axis
        if symbol == arcade.key.S:
            self.person.change_y += PLAYER_MOVEMENT_SPEED  # y-axis


def main():
    window = Game(WIDTH, HEIGHT, 'RmPG')
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()

'''
to-do list

classes: sprite -> entity -> person | enemy, room - map, camera

Map generator
Player shooting
UI
Menu

'''
