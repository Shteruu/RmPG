import arcade
import math
from itertools import product
import random

PATH = ''  # A:\ProjectGame\RmPG\\'

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BACKGROUND_TEXTURE_SCALING = 1
BORDER_SCALING = 0.1
CAMERA_SCALING = 1
SCALING = 1

PLAYER_MOVEMENT_SPEED = 10

RIGHT_FACING = DOWN_RIGHT_FACING = 0
LEFT_FACING = DOWN_LEFT_FACING = 1
UP_LEFT_FACING = UP_FACING = UP_RIGHT_FACING = 2
DOWN_FACING = None

WALL_TEXTURE = 1024
TILE_SIZE = 100
MAX_TILES_IN_ROOM = 3
ROOM_SIZE = 5 # tiles
MIN_ROOM_SIZE = ROOM_SIZE//2 + 1
MAP_SIZE = ROOM_SIZE * TILE_SIZE * 25  # *1000+ supported (*300 recommended maximum)
ROOM_COUNT = MAP_SIZE // (ROOM_SIZE * TILE_SIZE)

WALLS_SCALING = 0.1


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


class Tile:
    def __init__(self, width=TILE_SIZE, height=TILE_SIZE):
        self.width = width
        self.height = height
        self.room_id = 0

        # clockwise


        # counterclockwise
        self.right_backward = 0
        self.left_backward = 0
        self.up_backward = 0
        self.down_backward = width


class Room:
    def __init__(self, width=ROOM_SIZE, height=ROOM_SIZE):
        self.width = width
        self.height = height
        self.exist = False
        self.visited = False
        self.room_id = 0

        self.right = False
        self.left = False
        self.up = False
        self.down = False


class Game(arcade.Window):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)

        self.person = None

        self.physics_engine = None

        self.scene = None

        self.background_texture = None
        self.background_sprites_matrix = None

        self.map_matrix = None

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

        self.setup_background()

        self.scene.add_sprite_list("Walls", True)
        self.setup_border("Walls")

        self.map_generator()
        self.draw_map("Walls")

        self.scene.add_sprite_list("Player")
        self.person = Player()
        self.person.center_x = 1000
        self.person.center_y = 1000
        self.person.center = self.person.center_x, self.person.center_y

        self.scene.add_sprite("Player", self.person)
        self.scene.add_sprite_list(f"{PATH}sprites\\Forward.png")

        self.physics_engine = arcade.PhysicsEngineSimple(self.person, self.scene["Walls"])

    def setup_background(self):
        # setup texture
        self.background_texture = arcade.load_texture(f"{PATH}sprites\\2.png")

        # scaling texture
        self.background_texture.scaled_width = int(self.background_texture.width * BACKGROUND_TEXTURE_SCALING)
        self.background_texture.scaled_height = int(self.background_texture.height * BACKGROUND_TEXTURE_SCALING)

        # calculate matrix
        num_tiles_x = MAP_SIZE // self.background_texture.scaled_width + 1
        num_tiles_y = MAP_SIZE // self.background_texture.scaled_height + 1

        # setup matrix
        self.background_sprites_matrix = arcade.SpriteList()
        for x, y in product(range(num_tiles_x), range(num_tiles_y)):
            sprite = arcade.SpriteSolidColor(self.background_texture.scaled_width,
                                             self.background_texture.scaled_height, arcade.color.WHITE)
            sprite.texture = self.background_texture
            sprite.center_x = x * self.background_texture.scaled_width + self.background_texture.scaled_width / 2
            sprite.center_y = y * self.background_texture.scaled_height + self.background_texture.scaled_height / 2
            self.background_sprites_matrix.append(sprite)

    def draw_background(self):
        self.background_sprites_matrix.draw()

    def setup_border(self, name):
        """
        Append an edges walls to the scene_sprite_list *name*.
        """
        border_list = arcade.SpriteList()
        texture_width = int(WALL_TEXTURE * BORDER_SCALING)
        half_texture = texture_width // 2 + 1
        for x in range(0, MAP_SIZE, texture_width):
            coordinate_list = [[x + half_texture, half_texture],
                               [MAP_SIZE - half_texture, x + half_texture],
                               [MAP_SIZE - x + half_texture, MAP_SIZE - half_texture],
                               [half_texture, x + half_texture]]
            for coordinate in coordinate_list:
                wall = arcade.Sprite(f"{PATH}sprites\\wall.png", BORDER_SCALING)
                wall.center_x = coordinate[0]
                wall.center_y = coordinate[1]
                border_list.append(wall)
        self.scene.add_sprite_list(name, True, border_list)

    def map_generator(self):
        min_size = ROOM_SIZE // 2
        # сначала заполнять None, потом рандомить Tile
        self.map_matrix = [[Room() for _ in range(ROOM_COUNT)] for _ in range(ROOM_COUNT)]

        self.map_matrix[0][0].exist = True
        self.map_matrix[0][0].visited = True
        self.map_matrix[0][0].room_id = 1
        self.create_room(i=0, j=0)

        last_id = self.map_matrix[0][0].room_id
        for i in range(ROOM_COUNT):
            for j in range(ROOM_COUNT):
                if not self.map_matrix[i][j].visited:
                    self.map_matrix[i][j].visited = True
                    if random.getrandbits(1):
                        self.map_matrix[i][j].exist = True
                        last_id += 1
                        self.map_matrix[i][j].room_id = last_id
                        self.create_room(i, j)
        self.neighbour_check()

    def create_room(self, i, j, current_count=1):
        queue = [(i, j)]
        pointer = 0

        processing = True
        while processing:
            i = queue[pointer][0]
            j = queue[pointer][1]

            if current_count == MAX_TILES_IN_ROOM: break
            if i + 1 < ROOM_COUNT:
                if not self.map_matrix[i + 1][j].visited:
                    self.map_matrix[i + 1][j].visited = True
                    if random.getrandbits(1):
                        self.map_matrix[i + 1][j].exist = True
                        self.map_matrix[i + 1][j].width = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i + 1][j].height = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i + 1][j].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i + 1, j))

            if current_count == MAX_TILES_IN_ROOM: break
            if i - 1 >= 0:
                if not self.map_matrix[i - 1][j].visited:
                    self.map_matrix[i - 1][j].visited = True
                    if random.getrandbits(1):
                        self.map_matrix[i - 1][j].exist = True
                        self.map_matrix[i - 1][j].width = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i - 1][j].height = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i - 1][j].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i - 1, j))

            if current_count == MAX_TILES_IN_ROOM: break
            if j + 1 < ROOM_COUNT:
                if not self.map_matrix[i][j + 1].visited:
                    self.map_matrix[i][j + 1].visited = True
                    if random.getrandbits(1):
                        self.map_matrix[i][j + 1].exist = True
                        self.map_matrix[i][j + 1].width = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i][j + 1].height = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i][j + 1].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i, j + 1))

            if current_count == MAX_TILES_IN_ROOM: break
            if j - 1 >= 0:
                if not self.map_matrix[i][j - 1].visited:
                    self.map_matrix[i][j - 1].visited = True
                    if random.getrandbits(1):
                        self.map_matrix[i][j - 1].exist = True
                        self.map_matrix[i][j - 1].width = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i][j - 1].height = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i][j - 1].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i, j - 1))

            if pointer == len(queue) - 1: processing = False
            pointer += 1

    def neighbour_check(self):
        for i in range(ROOM_COUNT-1):
            for j in range(ROOM_COUNT-1):
                if self.map_matrix[i + 1][j].room_id == self.map_matrix[i][j].room_id:
                    self.map_matrix[i][j].height = self.map_matrix[i + 1][j].height

                if self.map_matrix[i][j + 1].room_id == self.map_matrix[i][j].room_id:
                    self.map_matrix[i][j].width = self.map_matrix[i][j + 1].width

    def draw_map(self, name):
        wall_list = arcade.SpriteList()  # correct!!
        for i in range(ROOM_COUNT):
            for j in range(ROOM_COUNT):
                if self.map_matrix[i][j].exist:
                    coordinate_list = []

                    if i + 1 < ROOM_COUNT:
                        if self.map_matrix[i + 1][j].room_id == self.map_matrix[i][j].room_id:
                            for y in range(0, self.map_matrix[i][j].height - self.map_matrix[i + 1][j].height): # right
                                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE + self.map_matrix[i][j].width * TILE_SIZE,
                                                     (self.map_matrix[i][j].height - y) * TILE_SIZE + j * TILE_SIZE * ROOM_SIZE)]
                        else:
                            for y in range(0, self.map_matrix[i][j].height + 1):  # right
                                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE + self.map_matrix[i][j].width * TILE_SIZE,
                                                     y * TILE_SIZE + j * TILE_SIZE * ROOM_SIZE)]
# родительская ширина и высота криво генерит
                    if i - 1 >= 0:
                        if self.map_matrix[i - 1][j].room_id == self.map_matrix[i][j].room_id:
                            for y in range(0, self.map_matrix[i][j].height - self.map_matrix[i - 1][j].height): # left
                                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE,
                                                    (self.map_matrix[i][j].height - y) * TILE_SIZE + j * TILE_SIZE * ROOM_SIZE)]
                        else:
                            for y in range(0, self.map_matrix[i][j].height + 1):  # left
                                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE,
                                                     y * TILE_SIZE + j * TILE_SIZE * ROOM_SIZE)]

                    if j + 1 < ROOM_COUNT: # сверху карты можно выйти (и справа)
                        if self.map_matrix[i][j + 1].room_id == self.map_matrix[i][j].room_id:
                            for x in range(0, self.map_matrix[i][j].width - self.map_matrix[i][j + 1].width):  # up
                                coordinate_list += [((self.map_matrix[i][j].width - x) * TILE_SIZE + i * TILE_SIZE * ROOM_SIZE,
                                                     j * TILE_SIZE * ROOM_SIZE + self.map_matrix[i][j].height * TILE_SIZE)]
                        else:
                            for x in range(0, self.map_matrix[i][j].width + 1):  # up
                                coordinate_list += [(x * TILE_SIZE + i * TILE_SIZE * ROOM_SIZE,
                                                     j * TILE_SIZE * ROOM_SIZE + self.map_matrix[i][j].height * TILE_SIZE)]
                    if j - 1 >= 0:
                        if self.map_matrix[i][j - 1].room_id == self.map_matrix[i][j].room_id:
                            for x in range(0, self.map_matrix[i][j].width - self.map_matrix[i][j - 1].width):  # down
                                coordinate_list += [((self.map_matrix[i][j].width - x) * TILE_SIZE + i * TILE_SIZE * ROOM_SIZE,
                                                     j * TILE_SIZE * ROOM_SIZE)]
                        else:
                            for x in range(0, self.map_matrix[i][j].width + 1):  # down
                                coordinate_list += [(x * TILE_SIZE + i * TILE_SIZE * ROOM_SIZE,
                                                     j * TILE_SIZE * ROOM_SIZE)]

                    for coordinate in coordinate_list:
                        wall = arcade.Sprite(f"{PATH}sprites\\wall.png", 0.9765625*WALLS_SCALING)
                        wall.center_x = coordinate[0]
                        wall.center_y = coordinate[1]
                        wall_list.append(wall)
        self.scene.add_sprite_list(name, True, wall_list)

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

        # I don't know how it worked, most likely the coordinates of the vector are calculated depending on the screen
        self.camera.move_to(
            (self.camera_x * CAMERA_SCALING, self.camera_y * CAMERA_SCALING),  # vector
            min(0.1 * CAMERA_SCALING, 1)
        )

    def on_draw(self):
        arcade.start_render()

        self.camera.use()

        self.draw_background()

        self.scene.draw()

    def on_update(self, delta_time: float):
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
        if symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.person.correct_change_x += -PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.person.correct_change_x += PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.person.correct_change_y += -PLAYER_MOVEMENT_SPEED  # y-axis
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.person.correct_change_y += PLAYER_MOVEMENT_SPEED  # y-axis

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.person.correct_change_x += PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.person.correct_change_x += -PLAYER_MOVEMENT_SPEED  # x-axis
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.person.correct_change_y += PLAYER_MOVEMENT_SPEED  # y-axis
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.person.correct_change_y += -PLAYER_MOVEMENT_SPEED  # y-axis


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

boolean WASD check ???
max speed exception
Map generator
Player shooting
UI
Menu
setup_textures ???

room generator
есть сетка генерации комнат 800х800, в которой генерируются части комнат
случайный x,y размеры в пределах 
половина сетки + корридор (200) < x,y < сетка
корридоры строго по середине квадрата сетки

генерация двумя вложенными циклами 
    генерация вглубь комнаты, 
    вероятность следующей комнаты умножается на номер потомка или
    или зависит от расстояния (в клетках) до комнаты-корня
    динамическая вероятность (что-то вроде экспаненты) вероятность//кол-во присоединенных клеток

случайно вибирается одно из 2 состояний каждой стороны квадрата сетки
- соседствует
- не соседствует
далее заполняется матрицей, которая проверяет есть ли связь с соседями, 
если да, создает ещё часть комнаты
+ проверка на лимит соседей
Если соседей не найдено происходят проверки
- будет ли в этом квадрате комната
    -  рандомит связи с соседними ЕЩЁ НЕ ПРОЙДЕННЫМИ комнатами


'''

# Если одновременно нажать на W и S - нельзя ходить вбок, а если A и D, то движение вверх-вниз работает как исправить
