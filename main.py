import arcade
import math
from itertools import product

PATH = ''  # A:\ProjectGame\RmPG\\'

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BACKGROUND_TEXTURE_SCALING = 1
BORDER_SCALING = 0.1
CAMERA_SCALING = 1
SCALING = 1

PLAYER_MOVEMENT_SPEED = 5

RIGHT_FACING = DOWN_RIGHT_FACING = 0
LEFT_FACING = DOWN_LEFT_FACING = 1
UP_LEFT_FACING = UP_FACING = UP_RIGHT_FACING = 2
DOWN_FACING = None

MAP_SIZE = 1024 * 70


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
        # loading textures
        self.stay_texture_pair = load_crop_texture_pair(f"{PATH}sprites\\Forward.png", 64, 64)
        self.stay_texture_pair.append(arcade.load_texture(f"{PATH}sprites\\Back.png"))
        self.texture_back = arcade.load_texture(f"{PATH}sprites\\Back.png")
        self.walk_textures = []
        for i in range(4):
            texture = load_crop_texture_pair(f"{PATH}sprites\\Forward.png", 64, 64, x=i * 64)
            self.walk_textures.append(texture)
        self.walk_textures.append(self.texture_back)
        # set start texture
        self.texture = self.stay_texture_pair[RIGHT_FACING]

        # for Player movement
        self.correct_change_x = 0
        self.correct_change_y = 0

    def update_animation(self, delta_time: float = 1 / 1):
        # standing still inspection
        if self.correct_change_x == 0 and self.correct_change_y == 0:
            self.texture = self.stay_texture_pair[self.facing]
            return
        # back have only one texture
        if self.facing == UP_FACING:
            self.texture = self.walk_textures[-1]
            return
        # running animation
        self.cur_texture += 1
        if self.cur_texture > 27:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture // 7][self.facing]


class Game(arcade.Window):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)

        self.person = None

        self.physics_engine = None

        self.scene = None

        self.background_texture = None

        self.bg_tile_sprites = None

        self.map = None

        self.border_wall_list = None

        self.camera = None

        self.camera_x = 0
        self.camera_y = 0

        self.mouse_angle = 0
        self.mouse_x = 0
        self.mouse_y = 0

    def setup(self):

        self.scene = arcade.Scene()

        self.camera = arcade.Camera(self.width, self.height)
        self.camera.viewport_width = SCREEN_WIDTH * CAMERA_SCALING
        self.camera.viewport_height = SCREEN_HEIGHT * CAMERA_SCALING

        self.background_texture = arcade.load_texture(f"{PATH}sprites\\2.png")
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

        self.setup_bg()

        self.person = Player()
        self.person.center_x = SCREEN_WIDTH // 2
        self.person.center_y = SCREEN_HEIGHT // 2
        self.person.center = self.person.center_x, self.person.center_y

        self.scene.add_sprite("Player", self.person)
        self.scene.add_sprite_list(f"{PATH}sprites\\Forward.png")

        self.scene.add_sprite_list("Walls", True, self.border_wall_list)
        self.border_wall_list = arcade.SpriteList()
        self.append_border("Walls")

        self.physics_engine = arcade.PhysicsEngineSimple(self.person, self.scene["Walls"])

    def append_border(self, name):
        """
        Append an edges walls to the sprite_list *name*.
        """
        texture_width = int(1024 * BORDER_SCALING)
        half_texture = texture_width // 2 + 1
        for x in range(0, MAP_SIZE, texture_width):
            coordinate_list = [[x + half_texture, half_texture],
                               [x + half_texture, MAP_SIZE - half_texture],
                               [half_texture, x + half_texture],
                               [MAP_SIZE - half_texture, x + half_texture]]
            for coordinate in coordinate_list:
                wall = arcade.Sprite("sprites\\wall.png", BORDER_SCALING)
                wall.center_x = coordinate[0]
                wall.center_y = coordinate[1]
                self.border_wall_list.append(wall)
        self.scene.add_sprite_list(name, True, self.border_wall_list)

    def setup_bg(self):
        # scaling texture
        self.background_texture.scaled_width = int(self.background_texture.width * BACKGROUND_TEXTURE_SCALING)
        self.background_texture.scaled_height = int(self.background_texture.height * BACKGROUND_TEXTURE_SCALING)
        # calculate matrix
        num_tiles_x = MAP_SIZE // self.background_texture.scaled_width + 1
        num_tiles_y = MAP_SIZE // self.background_texture.scaled_height + 1
        # setup matrix
        self.bg_tile_sprites = []
        for x, y in product(range(num_tiles_x), range(num_tiles_y)):
            sprite = arcade.SpriteSolidColor(self.background_texture.scaled_width,
                                             self.background_texture.scaled_height, arcade.color.WHITE)
            sprite.texture = self.background_texture
            sprite.center_x = x * self.background_texture.scaled_width + self.background_texture.scaled_width / 2
            sprite.center_y = y * self.background_texture.scaled_height + self.background_texture.scaled_height / 2
            self.bg_tile_sprites.append(sprite)

    def draw_background(self):
        # Создаем sprite batch
        sprite_batch = arcade.SpriteList()

        # Добавляем спрайты тайлов в sprite batch
        for sprite in self.bg_tile_sprites:
            sprite_batch.append(sprite)

        # Отрисовываем sprite batch
        sprite_batch.draw()

    def on_mouse(self):

        self.mouse_angle = math.atan2(self.mouse_y - (self.person.center_y - self.camera_y),
                                      self.mouse_x - (self.person.center_x - self.camera_x)) * 180 / math.pi

        if self.mouse_angle > 135 or self.mouse_angle < -90:
            self.person.facing = LEFT_FACING
        elif -90 <= self.mouse_angle < 45:
            self.person.facing = RIGHT_FACING
        elif 45 <= self.mouse_angle <= 135:
            self.person.facing = UP_FACING

        self.person.update_animation(1 / 60)

    def camera_on_player(self):  # coordinates links to left-down corner
        # calculate camera position
        screen_x = self.person.center_x - (SCREEN_WIDTH // 2) // CAMERA_SCALING
        screen_y = self.person.center_y - (SCREEN_HEIGHT // 2) // CAMERA_SCALING
        # outboard inspection
        self.camera_x = max(min(screen_x, MAP_SIZE - SCREEN_WIDTH // CAMERA_SCALING), 0)
        self.camera_y = max(min(screen_y, MAP_SIZE - SCREEN_HEIGHT // CAMERA_SCALING), 0)

        # сам не знаю, как это заработало скорее всего координаты вектора считаются в зависимости от экрана
        self.camera.move_to((self.camera_x * CAMERA_SCALING,
                             self.camera_y * CAMERA_SCALING),
                            min(0.1 * CAMERA_SCALING, 1))

    def get_current_room(self):
        x1, y1, x2, y2 = -1, -1, -1, -1
        for i in range(1000):
            x1 += 1
            x2 += 2
            y1 += 1
            y2 += 2
            if x1 <= self.person.center_x < x2 and y1 <= self.person.center_y < y2:
                return
        return None

    def on_draw(self):
        arcade.start_render()

        self.camera.use()

        self.draw_background()

        self.scene.draw()

    def on_update(self, delta_time: float):
        self.get_current_room()

        self.person.center_x += self.person.correct_change_x
        self.person.center_y += self.person.correct_change_y

        self.physics_engine.update()

        self.on_mouse()
        self.person.update_animation(delta_time)

        self.camera_on_player()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.person.correct_change_x += -PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.D:
            self.person.correct_change_x += PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.S:
            self.person.correct_change_y += -PLAYER_MOVEMENT_SPEED  # y-axis
        if symbol == arcade.key.W:
            self.person.correct_change_y += PLAYER_MOVEMENT_SPEED  # y-axis

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.person.correct_change_x += PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.D:
            self.person.correct_change_x += -PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.S:
            self.person.correct_change_y += PLAYER_MOVEMENT_SPEED  # y-axis
        if symbol == arcade.key.W:
            self.person.correct_change_y += -PLAYER_MOVEMENT_SPEED  # y-axis


# Если одновременно нажать на W и S - нельзя ходить вбок, а если A и D, то движение вверх-вниз работает


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
camera box 

'''
