import arcade

WIDTH = 800
HEIGHT = 600

PLAYER_MOVEMENT_SPEED = 3

RIGHT_FACING = DOWN_RIGHT_FACING = 0
LEFT_FACING = DOWN_LEFT_FACING = 1
UP_LEFT_FACING = UP_FACING = UP_RIGHT_FACING = 2
DOWN_FACING = None


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

        self.facing = RIGHT_FACING
        self.cur_texture = 0

        self.stay_texture_pair = load_crop_texture_pair("sprites/Forward.png", 64, 64)

        self.walk_textures = []
        for i in range(4):
            texture = load_crop_texture_pair("sprites/Forward.png", 64, 64, x=i*64)
            self.walk_textures.append(texture)

        self.sprite = None
        self.texture = self.stay_texture_pair[RIGHT_FACING]

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.stay_texture_pair[LEFT_FACING]
            return

        self.cur_texture += 1
        if self.cur_texture > 27:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture//7][self.facing]


class Player(Entity):

    def __init__(self):
        super().__init__()


class Game(arcade.Window):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)
        arcade.set_background_color(arcade.color.WHITE)

        self.scene = None

        self.physics_engine = None

        self.person = None

        self.map = None

    def setup(self):
        self.scene = arcade.Scene()

        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Map")

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

    def on_mouse_motion(self, x, y, dx, dy):
        if y > self.person.center_y and self.person.facing != UP_FACING:
            """self.person.facing = UP_FACING #пока нет текстуры в паке"""
        elif y < self.person.center_y and self.person.facing == UP_FACING:
            if x > self.person.center_x and self.person.facing != RIGHT_FACING:
                self.person.facing = RIGHT_FACING
            elif x < self.person.center_x and self.person.facing != LEFT_FACING:
                self.person.facing = LEFT_FACING

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

загружать текстуры игрока в __init__ ИГРОКА!!!

Map generator
Player shooting
UI
Menu

'''
