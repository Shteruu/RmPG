
import arcade
import arcade.gui
import math
from itertools import product
import random
from ctypes  import *



PATH = 'A:\ProjectGame\RmPG\\'  # A:\ProjectGame\RmPG\\'
SCREEN_TITLE = "RmPG"
SCREEN_WIDTH = windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = windll.user32.GetSystemMetrics(1)

BACKGROUND_TEXTURE_SCALING = 1
BORDER_SCALING = 0.1
CAMERA_SCALING = 1
SCALING = 1

PLAYER_MOVEMENT_SPEED = 10

RIGHT_FACING = DOWN_RIGHT_FACING = 0
LEFT_FACING = DOWN_LEFT_FACING = 1
UP_LEFT_FACING = UP_FACING = UP_RIGHT_FACING = 2
DOWN_FACING = None

MAP_SIZE = 1024 * 5 # *1000+ supported (*300 recommended maximum)
TILE_SIZE = 800
CORRIDOR_SIZE = 200
MAX_TILES_IN_ROOM = 10
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

class PauseMenu(arcade.gui.UIBoxLayout):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)
        arcade.gui.UIFlatButton(text="Нажми меня!", width=200)
        
       

    def on_close(self):
        
        super().on_close() 

        
        
class StartScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture(f"{PATH}sprites/i.png")
    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_text("Добро пожаловать в игру!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Нажмите 'Пробел', чтобы начать", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            arcade.close_window()
            window = GameView(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE )
            window.setup()
            arcade.run()





        
               
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
    def __init__(self, width=800, height=800):
        self.width = width
        self.height = height
        self.exist = False
        self.visited = False
        self.room_id = 0
        self.right = height
        self.left = height
        self.up = width
        self.down = width


class GameView(arcade.Window):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)

        self.person = None

        self.physics_engine = None

        self.scene = None

        self.background_texture = None
        self.background_sprites_matrix = None

        self.map_matrix = None
        self.tiles_count = None

        self.camera = None

        self.camera_x = 0
        self.camera_y = 0

        self.mouse_angle = 0
        self.mouse_x = 0
        self.mouse_y = 0
        
        
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.pause_menu = PauseMenu()
        self.is_paused = False
       
    
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
        self.person.center_x = 200
        self.person.center_y = 200
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
        texture_width = int(1024 * BORDER_SCALING)
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
        self.tiles_count = MAP_SIZE // TILE_SIZE
        min_size = TILE_SIZE//2 + CORRIDOR_SIZE//2
        #сначала заполнять None, потом рандомить Tile
        self.map_matrix = [[
                Tile(width=random.randint(min_size, TILE_SIZE)//10 * 10,
                     height=random.randint(min_size, TILE_SIZE)//10 * 10)
                for _ in range(self.tiles_count)]
                for _ in range(self.tiles_count)]

        self.map_matrix[0][0].exist = True
        self.map_matrix[0][0].visited = True
        self.map_matrix[0][0].room_id = 1
        self.create_room(i=0, j=0)

        last_id = self.map_matrix[0][0].room_id
        for i in range(self.tiles_count):
            for j in range(self.tiles_count):
                if not self.map_matrix[i][j].visited:
                    self.map_matrix[i][j].exist = random.getrandbits(1)
                    self.map_matrix[i][j].visited = True
                    if self.map_matrix[i][j].exist:
                        last_id += 1
                        self.map_matrix[i][j].room_id = last_id
                        self.create_room(i, j)

    def create_room(self, i, j, current_count=1):   
        queue = [(i, j)]
        pointer = 0

        processing = True
        while processing:
            i = queue[pointer][0]
            j = queue[pointer][1]

            if current_count == MAX_TILES_IN_ROOM: break
            if i + 1 < self.tiles_count:
                if not self.map_matrix[i+1][j].visited:
                    self.map_matrix[i+1][j].visited = 1
                    self.map_matrix[i+1][j].exist = random.getrandbits(1)
                    if self.map_matrix[i+1][j].exist:
                        self.map_matrix[i+1][j].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i + 1, j))
                        self.neighbour_check(i + 1, j)

            if current_count == MAX_TILES_IN_ROOM: break
            if i - 1 >= 0:
                if not self.map_matrix[i-1][j].visited:
                    self.map_matrix[i-1][j].visited = 1
                    self.map_matrix[i-1][j].exist = random.getrandbits(1)
                    if self.map_matrix[i - 1][j].exist:
                        self.map_matrix[i - 1][j].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i-1, j))
                        self.neighbour_check(i-1, j)

            if current_count == MAX_TILES_IN_ROOM: break
            if j + 1 < self.tiles_count:
                if not self.map_matrix[i][j+1].visited:
                    self.map_matrix[i][j+1].visited = 1
                    self.map_matrix[i][j+1].exist = random.getrandbits(1)
                    if self.map_matrix[i][j+1].exist:
                        self.map_matrix[i][j+1].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i, j+1))
                        self.neighbour_check(i, j+1)


            if current_count == MAX_TILES_IN_ROOM: break
            if j - 1 >= 0:
                if not self.map_matrix[i][j-1].visited:
                    self.map_matrix[i][j-1].visited = 1
                    self.map_matrix[i][j-1].exist = random.getrandbits(1)
                    if self.map_matrix[i][j-1].exist:
                        self.map_matrix[i][j-1].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i, j-1))
                        self.neighbour_check(i, j-1)

            if pointer == len(queue) - 1: processing = False
            pointer += 1

    def neighbour_check(self, i, j):
        if i + 1 < self.tiles_count: # r
            if self.map_matrix[i+1][j].room_id == self.map_matrix[i][j].room_id:
                self.map_matrix[i + 1][j].right = self.map_matrix[i][j].height
                self.map_matrix[i + 1][j].height = self.map_matrix[i][j].height
                self.map_matrix[i+1][j].left = 0
                self.map_matrix[i][j].right = 0

                self.map_matrix[i][j].up = TILE_SIZE
                self.map_matrix[i][j].down = TILE_SIZE

        if i - 1 >= 0: # l
            if self.map_matrix[i-1][j].room_id == self.map_matrix[i][j].room_id:
                self.map_matrix[i - 1][j].left = self.map_matrix[i][j].height
                self.map_matrix[i - 1][j].height = self.map_matrix[i][j].height
                self.map_matrix[i-1][j].right = 0
                self.map_matrix[i][j].left = 0

                self.map_matrix[i-1][j].up = TILE_SIZE
                self.map_matrix[i-1][j].down = TILE_SIZE

        if j + 1 < self.tiles_count: # up
            if not self.map_matrix[i][j+1].room_id == self.map_matrix[i][j].room_id:
                self.map_matrix[i][j + 1].up = self.map_matrix[i][j].width
                self.map_matrix[i][j + 1].width = self.map_matrix[i][j].width
                self.map_matrix[i][j+1].down = 0
                self.map_matrix[i][j].up = 0

                self.map_matrix[i][j].left = TILE_SIZE
                self.map_matrix[i][j].right = TILE_SIZE

        if j - 1 >= 0: # down
            if not self.map_matrix[i][j-1].room_id == self.map_matrix[i][j].room_id:
                self.map_matrix[i][j].down = self.map_matrix[i][j - 1].width
                self.map_matrix[i][j - 1].width = self.map_matrix[i][j].width
                self.map_matrix[i][j-1].up = 0
                self.map_matrix[i][j].down = 0

                self.map_matrix[i][j-1].left = TILE_SIZE
                self.map_matrix[i][j-1].right = TILE_SIZE

    def draw_map(self, name):
        for i in range(self.tiles_count):
            for j in range(self.tiles_count):
                if self.map_matrix[i][j].exist:
                    wall_list = arcade.SpriteList()
                    texture_width = int(1024 * WALLS_SCALING)
                    half_texture = texture_width // 2
                    coordinate_list = []

                    for x in range(half_texture, self.map_matrix[i][j].down, texture_width): #down
                        coordinate_list += [(x + i * TILE_SIZE, j * TILE_SIZE)]

                    for y in range(half_texture, self.map_matrix[i][j].left, texture_width): #left
                        coordinate_list += [(i * TILE_SIZE, y + j * TILE_SIZE)]

                    for x in range(half_texture, self.map_matrix[i][j].up, texture_width): #up
                        coordinate_list += [(i * TILE_SIZE + x,
                                             j * TILE_SIZE + self.map_matrix[i][j].height)]

                    for y in range(half_texture, self.map_matrix[i][j].right, texture_width): #right
                        coordinate_list += [(i * TILE_SIZE + self.map_matrix[i][j].width,
                                             j * TILE_SIZE + y)]


        for coordinate in coordinate_list:
                        wall = arcade.Sprite(f"{PATH}sprites\\wall.png", WALLS_SCALING)
                        wall.center_x = coordinate[0]
                        wall.center_y = coordinate[1]
                        wall_list.append(wall)
        self.scene.add_sprite_list(name, True, wall_list)
        
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.manager.add(self.pause_menu)
        else:
            self.manager.remove(self.pause_menu)

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
            (self.camera_x * CAMERA_SCALING, self.camera_y * CAMERA_SCALING), # vector
            min(0.1 * CAMERA_SCALING, 1)
        )

    def on_draw(self):
        
        arcade.start_render()
        if self.is_paused:
            self.pause_menu.on_show()
        else:
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
        if symbol == arcade.key.ESCAPE:
            self.toggle_pause()
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
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE )
    start_screen = StartScreen()
    window.show_view(start_screen)
    arcade.run()


if __name__ == "__main__":
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



#Если одновременно нажать на W и S - нельзя ходить вбок, а если A и D, то движение вверх-вниз работает как исправить