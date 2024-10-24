import arcade
import math

PATH = ''#A:\ProjectGame\RmPG\\'

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCALING = 1

PLAYER_MOVEMENT_SPEED = 3

RIGHT_FACING = DOWN_RIGHT_FACING = 0
LEFT_FACING = DOWN_LEFT_FACING = 1
UP_LEFT_FACING = UP_FACING = UP_RIGHT_FACING = 2
DOWN_FACING = None

MAP_SIZE = 1000


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


class Player(Entity):

    def __init__(self):
        super().__init__()
        self.stay_texture_pair = load_crop_texture_pair(f"{PATH}sprites\\Forward.png", 64, 64)
        self.stay_texture_pair.append(arcade.load_texture(f"{PATH}sprites\\Back.png"))

        self.texture_back = arcade.load_texture(f"{PATH}sprites\\Back.png")
        self.walk_textures = []
        for i in range(4):
            texture = load_crop_texture_pair(f"{PATH}sprites\\Forward.png", 64, 64, x=i * 64)
            self.walk_textures.append(texture)
        self.walk_textures.append(self.texture_back)

        self.sprite = None
        self.texture = self.stay_texture_pair[RIGHT_FACING]

    def update_animation(self, delta_time: float = 1 / 1):
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.stay_texture_pair[self.facing]
            return
        if self.facing == UP_FACING:
            self.texture = self.walk_textures[-1]
            return
        self.cur_texture += 1
        if self.cur_texture > 27:
            self.cur_texture = 0

        self.texture = self.walk_textures[self.cur_texture // 7][self.facing]


class Game(arcade.Window):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)

        self.background_texture = None

        self.scene = None

        self.physics_engine = None

        self.person = None

        self.map = None

        self.mouse_angle = 0
        self.mouse_x = 0
        self.mouse_y = 0

        self.camera = None


    def on_mouse(self):
        self.mouse_angle = math.atan2(self.mouse_y- self.person.center_y, self.mouse_x - self.person.center_x) * (180 / math.pi)
        if self.mouse_angle > 135 or self.mouse_angle < -90:
            self.person.facing = LEFT_FACING
        elif -90 <= self.mouse_angle < 45:
            self.person.facing = RIGHT_FACING
        elif 45 <= self.mouse_angle <= 135:
            self.person.facing = UP_FACING

        self.person.update_animation(1/60)

    def setup(self):
        self.scene = arcade.Scene()

        self.camera = arcade.Camera(self.width, self.height)
        self.camera.viewport_width = SCREEN_WIDTH * SCALING
        self.camera.viewport_height = SCREEN_HEIGHT * SCALING

        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Map")
        self.background_texture = arcade.load_texture(f"{PATH}sprites\\background.jpg")

        self.person = Player()
        # self.person.scale = 0.5
        self.person.center_x = SCREEN_WIDTH // 2
        self.person.center_y = SCREEN_HEIGHT // 2
        self.person.center = self.person.center_x, self.person.center_y

        self.scene.add_sprite("Player", self.person)
        self.scene.add_sprite_list(f"{PATH}sprites\\Forward.png")

    def camera_on_player(self):  # coordinates links to left-down corner
        screen_center_x = self.person.center_x - SCREEN_WIDTH // 2
        screen_center_y = self.person.center_y - SCREEN_HEIGHT // 2
        camera_x = max(min(screen_center_x, MAP_SIZE - SCREEN_WIDTH), 0)
        camera_y = max(min(screen_center_y, MAP_SIZE - SCREEN_HEIGHT), 0)

        self.camera.move_to((camera_x, camera_y))

    def on_draw(self):
        arcade.start_render()

        self.camera.use()

        arcade.draw_texture_rectangle(MAP_SIZE // 2, MAP_SIZE // 2, MAP_SIZE, MAP_SIZE, self.background_texture)

        self.scene.draw()

    def on_update(self, delta_time: float):
        self.person.center_x += self.person.change_x
        self.person.center_y += self.person.change_y
        self.on_mouse()
        self.person.update_animation(delta_time)

        self.camera_on_player()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y



    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.person.change_x += -PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.D:
            self.person.change_x += PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.W:
            self.person.change_y += PLAYER_MOVEMENT_SPEED  # y-axis
        if symbol == arcade.key.S:
            self.person.change_y += -PLAYER_MOVEMENT_SPEED  # y-axis

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
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, 'RmPG')
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()

'''
to-do list

classes: sprite -> entity -> enemy
         room - map

Map generator
Player shooting
UI
Menu

'''
