import arcade
import arcade.gui
import math
from itertools import product
import random
PATH = ''  # A:\ProjectGame\RmPG\\'

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PLAYER_MOVEMENT_SPEED = 8

RIGHT_FACING = DOWN_RIGHT_FACING = 0
LEFT_FACING = DOWN_LEFT_FACING = 1
UP_LEFT_FACING = UP_FACING = UP_RIGHT_FACING = 2
DOWN_FACING = None

WALL_TEXTURE = 1024
TILE_SIZE = 100
MAX_ROOM_SECTIONS = 8
ROOM_SIZE = 5 # tiles
MIN_ROOM_SIZE = ROOM_SIZE//2 + 1

BACKGROUND_TEXTURE_SCALING = 0.2
CAMERA_SCALING = 1
SCALING = 1
WALLS_SCALING = 0.9765625 # cause wall has 1024p texture and tile is 100p
WALLS_SCALING *= 0.001*TILE_SIZE


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


def append_wall_list(coordinate_list, wall_list):
    """
    append walls in arcade.SpriteList by coordinates {(i1, j1), (i2, j2)...}
    """
    for coordinate in coordinate_list:
        wall = arcade.Sprite(f"{PATH}sprites\\wall.png", WALLS_SCALING)
        wall.center_x = coordinate[0]
        wall.center_y = coordinate[1]
        wall_list.append(wall)


class StartMenu:
    def __init__(self, game):
        self.game = game
        self.screen_texture = arcade.load_texture(f"{PATH}sprites\\start_screen.png")
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()
        self.text_color = arcade.color.ANTI_FLASH_WHITE
        self.counter_color = arcade.color.ANTI_FLASH_WHITE

        # Create buttons
        self.start_button = arcade.gui.UIFlatButton(text="Start Game", width=240,
                                                    x=game.width // 2 - 120, y=game.height // 2)
        self.quit_button = arcade.gui.UIFlatButton(text="Quit", width=240,
                                                   x=game.width // 2 - 120, y=game.height // 2 - 60)

        # Create counter buttons
        self.room_count = game.room_count
        self.increase_button = arcade.gui.UIFlatButton(text=">", width=50,
                                                       x=game.width // 2 + 30, y=game.height // 2 - 120)
        self.decrease_button = arcade.gui.UIFlatButton(text="<", width=50,
                                                       x=game.width // 2 - 80, y=game.height // 2 - 120)

        self.much_increase_button = arcade.gui.UIFlatButton(text=">>", width=35,
                                                            x=game.width // 2 + 85, y=game.height // 2 - 120)
        self.much_decrease_button = arcade.gui.UIFlatButton(text="<<", width=35,
                                                            x=game.width // 2 - 120, y=game.height // 2 - 120)

        # Add event handlers
        self.start_button.on_click = self.on_start_game
        self.quit_button.on_click = self.on_quit
        self.increase_button.on_click = self.on_increase
        self.decrease_button.on_click = self.on_decrease
        self.much_increase_button.on_click = self.on_much_increase
        self.much_decrease_button.on_click = self.on_much_decrease

        # Add buttons to UI Manager
        self.ui_manager.add(self.start_button)
        self.ui_manager.add(self.quit_button)
        self.ui_manager.add(self.increase_button)
        self.ui_manager.add(self.decrease_button)
        self.ui_manager.add(self.much_increase_button)
        self.ui_manager.add(self.much_decrease_button)

    def on_start_game(self, event):
        self.game.current_state = "setup"  # Change to game state
        self.game.is_paused = False

    @staticmethod
    def on_quit(event):
        arcade.close_window()

    def on_increase(self, event):
        self.game.room_count += 1
        self.counter_check()

    def on_decrease(self, event):
        self.game.room_count -= 1
        self.counter_check()

    def on_much_increase(self, event):
        self.game.room_count += 10
        self.counter_check()

    def on_much_decrease(self, event):
        self.game.room_count -= 10
        self.counter_check()

    def counter_check(self):
        if self.game.room_count < 1:
            self.game.room_count = 1
            self.counter_color = arcade.color.RED
        elif self.game.room_count > 80:
            self.game.room_count = 80
            self.counter_color = arcade.color.RED
        else:
            self.counter_color = arcade.color.ANTI_FLASH_WHITE

    def draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                                      SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.screen_texture)

        arcade.draw_text("Let's play?",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, self.text_color,
                         font_size=24, anchor_x="center")

        arcade.draw_text(f"{self.game.room_count}",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 105, self.counter_color,
                         font_size=24, anchor_x="center")
        self.ui_manager.draw()

    def update(self):
        self.ui_manager.on_update(1 / 60)


class PauseMenu:
    def __init__(self, game):
        self.game = game
        self.visible = False
        self.inaccuracy = PLAYER_MOVEMENT_SPEED*10
        self.resume_button = arcade.gui.UIFlatButton(text="Resume", width=200,
                                                     x=game.width // 2 - 130, y=game.height // 2 + 8)
        self.quit_button = arcade.gui.UIFlatButton(text="Quit", width=200,
                                                   x=game.width // 2 - 130, y=game.height // 2 - 52)

        # Add button callbacks
        self.resume_button.on_click = self.on_resume
        self.quit_button.on_click = self.on_quit

        # Create a UI container
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()
        self.ui_manager.add(self.resume_button)
        self.ui_manager.add(self.quit_button)

    def on_resume(self, event):
        self.visible = False
        self.game.is_paused = False

    @staticmethod
    def on_quit(event):
        arcade.close_window()

    def draw(self):
        if self.visible:
            left = max(self.game.camera_x - self.inaccuracy, 0)
            right = min(self.game.camera_x + SCREEN_WIDTH + self.inaccuracy, self.game.map_size)
            up = min(self.game.camera_y + SCREEN_HEIGHT + self.inaccuracy, self.game.map_size)
            down = max(self.game.camera_y - self.inaccuracy, 0)

            arcade.draw_lrtb_rectangle_filled(left, right, up, down, (0, 0, 0, 128))

            self.ui_manager.draw()

    def update(self):
        if self.visible:
            self.ui_manager.on_update(1/60)
            

class FinalMenu:
    def __init__(self, game):
        self.game = game
        self.screen_texture = arcade.load_texture(f"{PATH}sprites\\start_screen.png")
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.play_again_button = arcade.gui.UIFlatButton(text="Play again", width=200,
                                                   x=game.width // 2 - 100, y=game.height // 2)
        self.quit_button = arcade.gui.UIFlatButton(text="Quit", width=200,
                                                   x=game.width // 2 - 100, y=game.height // 2 - 60)

        self.play_again_button.on_click = self.on_play_again
        self.quit_button.on_click = self.on_quit
        self.ui_manager.add(self.quit_button)
        self.ui_manager.add(self.play_again_button)
    
    @staticmethod
    def on_quit(event):
        arcade.close_window()

    def on_play_again(self, event):
        self.game.current_state = "menu"
        self.game.is_paused = True

    def draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                                      SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.screen_texture)
        arcade.draw_text("See you in the new adventures!",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, arcade.color.ANTI_FLASH_WHITE,
                         font_size=24, anchor_x="center")
        self.ui_manager.draw()

    def update(self):
        self.ui_manager.on_update(1 / 60)


class Player(arcade.Sprite):
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
        self.facing = RIGHT_FACING
        self.texture = self.stay_texture_pair[self.facing]
        self.cur_texture = 0

        # for Player movement
        self.correct_change_x = 0
        self.correct_change_y = 0

    def update_animation(self, delta_time: float = 1 / 60):
        # standing-still inspection
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


class Room:
    def __init__(self, width=ROOM_SIZE, height=ROOM_SIZE):
        self.width = width
        self.height = height
        self.exist = False
        self.visited = False
        self.room_id = 0


class Game(arcade.Window):
    def __init__(self, width, height, name):
        super().__init__(width, height, name)

        self.person = None

        self.scene = None
        self.camera = None

        self.camera_x = 0
        self.camera_y = 0

        self.physics_engine = None

        self.background_texture = None
        self.background_sprites_matrix = None

        self.map_matrix = None
        self.graph = None

        self.mouse_angle = 0
        self.mouse_x = 0
        self.mouse_y = 0

        self.room_count = 10
        self.map_size = ROOM_SIZE * TILE_SIZE * self.room_count  # ~100 - dfs recursion limit

        self.current_state = "menu"
        self.start_menu = StartMenu(self)
        self.pause_menu = PauseMenu(self)
        self.final_menu = FinalMenu(self)
        self.is_paused = True

        self.trinket_sprite_list = None
        self.score = 0
        self.trinket_amount = 0
        self.portal = None

    def setup(self):

        self.scene = arcade.Scene()

        self.camera = arcade.Camera(self.width, self.height)
        self.camera.viewport_width = SCREEN_WIDTH * CAMERA_SCALING
        self.camera.viewport_height = SCREEN_HEIGHT * CAMERA_SCALING

        self.setup_background()

        self.scene.add_sprite_list("Walls", True)
        self.portal = arcade.Sprite(f"{PATH}sprites\\portal.png", 0.52)

        self.setup_border("Walls")

        self.map_generator()
        self.graph = self.graph_builds
        self.draw_map("Walls")

        self.scene.add_sprite_list("Player")
        self.person = Player()
        self.person.center_x = TILE_SIZE * 1.5
        self.person.center_y = TILE_SIZE * 1.5
        self.person.center = self.person.center_x, self.person.center_y

        self.scene.add_sprite("Player", self.person)

        self.physics_engine = arcade.PhysicsEngineSimple(self.person, self.scene["Walls"])

        self.trinket_sprite_list = arcade.SpriteList()
        self.setup_trinket()
        self.score = 0

    def setup_background(self):
        """
        loading a background texture to background_sprites_matrix
        """
        # setup texture
        self.background_texture = arcade.load_texture(f"{PATH}sprites\\ComfyUI_5.png")

        # scaling texture
        self.background_texture.scaled_width = int(self.background_texture.width * BACKGROUND_TEXTURE_SCALING)
        self.background_texture.scaled_height = int(self.background_texture.height * BACKGROUND_TEXTURE_SCALING)

        # calculate matrix
        num_tiles_x = self.map_size // self.background_texture.scaled_width + 1
        num_tiles_y = self.map_size // self.background_texture.scaled_height + 1

        # setup matrix
        self.background_sprites_matrix = arcade.SpriteList()
        for x, y in product(range(num_tiles_x), range(num_tiles_y)):
            sprite = arcade.Sprite(scale=BACKGROUND_TEXTURE_SCALING)
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
        half = ROOM_SIZE * TILE_SIZE//2
        for i in range(self.room_count):
            # down
            wall = arcade.SpriteSolidColor(width=ROOM_SIZE*TILE_SIZE, height=50,
                                           color=arcade.color.BOSTON_UNIVERSITY_RED)
            wall.set_position(half + i * ROOM_SIZE * TILE_SIZE, -25)
            border_list.append(wall)

            # up
            wall = arcade.SpriteSolidColor(width=ROOM_SIZE*TILE_SIZE, height=50,
                                           color=arcade.color.BOSTON_UNIVERSITY_RED)
            wall.set_position(half + i * ROOM_SIZE * TILE_SIZE, self.map_size+25)
            border_list.append(wall)

            # left
            wall = arcade.SpriteSolidColor(width=50, height=ROOM_SIZE*TILE_SIZE,
                                           color=arcade.color.BOSTON_UNIVERSITY_RED)
            wall.set_position(-25, half + i * ROOM_SIZE * TILE_SIZE)
            border_list.append(wall)

            # right
            wall = arcade.SpriteSolidColor(width=50, height=ROOM_SIZE*TILE_SIZE,
                                           color=arcade.color.BOSTON_UNIVERSITY_RED)
            wall.set_position(self.map_size+25, half + i * ROOM_SIZE * TILE_SIZE)
            border_list.append(wall)

        self.scene.add_sprite_list(name, True, border_list)

    def map_generator(self):
        """
        randomly generate room matrix
        """
        self.map_matrix = [[Room() for _ in range(self.room_count)] for _ in range(self.room_count)]

        self.map_matrix[0][0].exist = True
        self.map_matrix[0][0].visited = True
        self.map_matrix[0][0].room_id = 1
        self.create_room(i=0, j=0)

        last_id = self.map_matrix[0][0].room_id
        for i in range(self.room_count):
            for j in range(self.room_count):
                if not self.map_matrix[i][j].visited:
                    self.map_matrix[i][j].visited = True
                    if random.getrandbits(1):
                        self.map_matrix[i][j].exist = True
                        last_id += 1
                        self.map_matrix[i][j].room_id = last_id
                        self.create_room(i, j)
        self.neighbour_check()

    def create_room(self, i, j, current_count=1):
        """
        creates small rooms around and gathers them into one large room
        """
        queue = [(i, j)]
        pointer = 0

        processing = True
        while processing:
            i = queue[pointer][0]
            j = queue[pointer][1]

            if current_count == MAX_ROOM_SECTIONS: break # reinsurance
            if i + 1 < self.room_count:
                if not self.map_matrix[i + 1][j].visited:
                    self.map_matrix[i + 1][j].visited = True
                    # if current_count >= MAX_TILES_IN_ROOM generator will stop
                    if random.getrandbits(MAX_ROOM_SECTIONS)//current_count:
                        self.map_matrix[i + 1][j].exist = True
                        self.map_matrix[i][j].width = ROOM_SIZE
                        self.map_matrix[i + 1][j].width = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i + 1][j].height = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i + 1][j].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i + 1, j))

            if current_count == MAX_ROOM_SECTIONS: break
            if i - 1 >= 0:
                if not self.map_matrix[i - 1][j].visited:
                    self.map_matrix[i - 1][j].visited = True
                    if random.getrandbits(MAX_ROOM_SECTIONS)//current_count:
                        self.map_matrix[i - 1][j].exist = True
                        self.map_matrix[i - 1][j].width = ROOM_SIZE
                        self.map_matrix[i - 1][j].height = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i - 1][j].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i - 1, j))

            if current_count == MAX_ROOM_SECTIONS: break
            if j + 1 < self.room_count:
                if not self.map_matrix[i][j + 1].visited:
                    self.map_matrix[i][j + 1].visited = True
                    if random.getrandbits(MAX_ROOM_SECTIONS)//current_count:
                        self.map_matrix[i][j + 1].exist = True
                        self.map_matrix[i][j].height = ROOM_SIZE
                        self.map_matrix[i][j + 1].width = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i][j + 1].height = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i][j + 1].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i, j + 1))

            if current_count == MAX_ROOM_SECTIONS: break
            if j - 1 >= 0:
                if not self.map_matrix[i][j - 1].visited:
                    self.map_matrix[i][j - 1].visited = True
                    if random.getrandbits(MAX_ROOM_SECTIONS)//current_count:
                        self.map_matrix[i][j - 1].exist = True
                        self.map_matrix[i][j - 1].width = random.randint(MIN_ROOM_SIZE, ROOM_SIZE)
                        self.map_matrix[i][j - 1].height = ROOM_SIZE
                        self.map_matrix[i][j - 1].room_id = self.map_matrix[i][j].room_id
                        current_count += 1
                        queue.append((i, j - 1))

            if pointer == len(queue) - 1: processing = False
            pointer += 1

    def neighbour_check(self):
        """
        Final lick check and rooms rebuild
        """
        for i in range(self.room_count-1):
            for j in range(self.room_count-1):

                f1 = f2 = False
                if self.map_matrix[i + 1][j].room_id == self.map_matrix[i][j].room_id: #right check
                    f1 = True
                if self.map_matrix[i][j + 1].room_id == self.map_matrix[i][j].room_id: #up check
                    f2 = True

                if f1 and not f2: # only right
                    self.map_matrix[i][j].height = self.map_matrix[i + 1][j].height
                    self.map_matrix[i][j].width = ROOM_SIZE #necessary part, bag fix

                if f2 and not f1: # only up
                    self.map_matrix[i][j].width = self.map_matrix[i][j + 1].width
                if f1 and f2:
                    self.map_matrix[i][j].height = ROOM_SIZE
                    self.map_matrix[i][j].width = ROOM_SIZE

        for i in range(self.room_count - 1): # right edge check
            if self.map_matrix[i + 1][self.room_count-1].room_id == self.map_matrix[i][self.room_count-1].room_id:
                self.map_matrix[i][self.room_count-1].width = ROOM_SIZE  # necessary part, bag fix

        for j in range(self.room_count - 1): #up edge check
            if self.map_matrix[self.room_count-1][j + 1].room_id == self.map_matrix[self.room_count-1][j].room_id:
                self.map_matrix[self.room_count-1][j].heigth = ROOM_SIZE  # necessary part, bag fix

    @property
    def graph_builds(self):
        """
        Create a graph from Room matrix
        :return: a graph from dictionaries
        """

        '''
        relation(i, j, direction)
        i, j - coordinates in room matrix
        '''

        # create an empty graph
        graph = {}
        for x in range(self.get_max_room_id()):
            graph[x + 1] = {}

        previous_i, previous_j = 0, 0
        # vertical relation
        for i in range(self.room_count):
            previous_id = None
            for j in range(self.room_count):
                if self.map_matrix[i][j].room_id:
                    correct_id = self.map_matrix[i][j].room_id
                    if previous_id is None:
                        previous_id = correct_id
                    if correct_id != previous_id:
                        graph[correct_id][previous_id] = (i, j, 0) # down
                        graph[previous_id][correct_id] = (previous_i, previous_j, 1) # up
                        previous_id = correct_id
                        previous_i, previous_j = i, j
                    else:
                        previous_i, previous_j = i, j

        # horizontal relation
        for j in range(self.room_count):
            previous_id = None
            for i in range(self.room_count):
                if self.map_matrix[i][j].room_id:
                    correct_id = self.map_matrix[i][j].room_id
                    if previous_id is None:
                        previous_id = correct_id
                    if correct_id != previous_id:
                        graph[correct_id][previous_id] = (i, j, 2) # left
                        graph[previous_id][correct_id] = (previous_i, previous_j, 3) # right
                        previous_id = correct_id
                        previous_i, previous_j = i, j
                    else:
                        previous_i, previous_j = i, j

        return graph

    def get_max_room_id(self):
        return max([self.map_matrix[i][j].room_id for i in range(self.room_count) for j in range(self.room_count)])

    def create_corridors(self):
        """
        creates corridors along the specified trace in graph
        :return: corridor coordinates
        """

        # create a trace
        corridors = set(self.dfs())
        corridors.update(self.rnd_add(0.25))

        trace = []
        for coord in corridors:
            trace.append(self.graph[coord[0]][coord[1]])
            trace.append(self.graph[coord[1]][coord[0]])

        # create corridors
        corridors_coordinates = []
        half_room = ROOM_SIZE // 2
        for value in trace:
            i, j = value[0], value[1]
            match value[2]:
                case 0:  # down direction
                    corridors_coordinates.append((i * TILE_SIZE * ROOM_SIZE + half_room * TILE_SIZE,
                                                  j * TILE_SIZE * ROOM_SIZE))

                case 1:  # up direction
                    corridors_coordinates.append((i * TILE_SIZE * ROOM_SIZE + half_room * TILE_SIZE,
                                                  (j * ROOM_SIZE + self.map_matrix[i][j].height) * TILE_SIZE))

                case 2:  # left direction
                    corridors_coordinates.append((i * TILE_SIZE * ROOM_SIZE,
                                                  j * TILE_SIZE * ROOM_SIZE + half_room * TILE_SIZE))

                case 3:  # right direction
                    corridors_coordinates.append(((i * ROOM_SIZE + self.map_matrix[i][j].width) * TILE_SIZE,
                                                  j * TILE_SIZE * ROOM_SIZE + half_room * TILE_SIZE))

        return corridors_coordinates

    @staticmethod
    def draw_corridors(corridors_coordinates):
        """
        builds corridor walls according to the coordinates
        :param corridors_coordinates:
        :return: a corridor's walls coordinates
        """
        corridor_list = arcade.SpriteList()
        coordinate_list_vert = set()
        coordinate_list_horiz = set()

        # setup
        for i in range(len(corridors_coordinates)//2):
            # horizontal
            if corridors_coordinates[i*2][0] == corridors_coordinates[i*2+1][0]:
                x = corridors_coordinates[i*2][0]
                m1 = min(corridors_coordinates[i * 2][1], corridors_coordinates[i * 2 + 1][1])
                m2 = max(corridors_coordinates[i * 2][1], corridors_coordinates[i * 2 + 1][1])
                for y in range(m1, m2+1, TILE_SIZE):
                    coordinate_list_vert.add((x, y))
            # vertical
            if corridors_coordinates[i * 2][1] == corridors_coordinates[i * 2 + 1][1]:
                y = corridors_coordinates[i * 2][1]
                m1 = min(corridors_coordinates[i * 2][0], corridors_coordinates[i * 2 + 1][0])
                m2 = max(corridors_coordinates[i * 2][0], corridors_coordinates[i * 2 + 1][0])
                for x in range(m1, m2+1, TILE_SIZE):
                    coordinate_list_horiz.add((x, y))

        # removing crossed tiles
        coordinate_remove = coordinate_list_horiz & coordinate_list_vert
        coordinate_list_horiz -= coordinate_remove
        coordinate_list_vert -= coordinate_remove

        # append vertical walls
        for coordinate in coordinate_list_vert:
            wall_l = arcade.Sprite(f"{PATH}sprites\\wall.png", WALLS_SCALING,
                                   image_width=112, image_height=1024)
            wall_r = arcade.Sprite(f"{PATH}sprites\\wall.png", WALLS_SCALING,
                                   image_width=112, image_height=1024,
                                   image_x=912)
            wall_l.center_x = coordinate[0] - TILE_SIZE//2 + 56*WALLS_SCALING
            wall_l.center_y = coordinate[1]
            wall_r.center_x = coordinate[0] + TILE_SIZE//2 - 56*WALLS_SCALING
            wall_r.center_y = coordinate[1]
            corridor_list.append(wall_l)
            corridor_list.append(wall_r)

        # append horizontal walls
        for coordinate in coordinate_list_horiz:
            wall_u = arcade.Sprite(f"{PATH}sprites\\wall.png", WALLS_SCALING,
                                   image_width=1024, image_height=112)
            wall_d = arcade.Sprite(f"{PATH}sprites\\wall.png", WALLS_SCALING,
                                   image_width=1024, image_height=112,
                                   image_y=912)
            wall_u.center_x = coordinate[0]
            wall_u.center_y = coordinate[1] - TILE_SIZE // 2 + 56*WALLS_SCALING
            wall_d.center_x = coordinate[0]
            wall_d.center_y = coordinate[1] + TILE_SIZE // 2 - 56*WALLS_SCALING
            corridor_list.append(wall_u)
            corridor_list.append(wall_d)

        return corridor_list

    def dfs(self, start=1, visited=None, edges=None):
        """
        Deep-first-search
        :param start: start vertex
        :param visited: utility
        :param edges: utility
        :return: trase [(i1, i2), (i2, i3)...]
        """
        graph = self.graph

        if visited is None:
            visited = set()  # Создаем множество для отслеживания посещенных узлов
        if edges is None:
            edges = []  # Список для хранения пройденных ребер

        visited.add(start)  # Помечаем текущий узел как посещенный

        # Рекурсивно обходим соседние узлы
        for neighbor in graph.get(start, {}):
            if neighbor not in visited:
                edges.append((start, neighbor))  # Сохраняем пройденное ребро
                self.dfs(neighbor, visited, edges)

        last_element = list(visited)[-1]
        lst = list(self.graph[last_element].values())
        if not bool(lst):
            self.portal.position = (TILE_SIZE * 4, TILE_SIZE * 4)
        if bool(lst):
            self.portal.position = (lst[0][0] * TILE_SIZE * ROOM_SIZE + TILE_SIZE * 2,
                                    lst[0][1] * TILE_SIZE * ROOM_SIZE + TILE_SIZE * 2)
        return edges  # return trace

    def rnd_add(self, chance=0.1):
        """
        randomly create a corridors
        :param chance: a chance to create each corridor
        :return: vertex connection {(i1, i2), (i2, i3)...}
        """
        edges = set()
        graph = self.graph
        for node, links in graph.items():
            for neighbor, attributes in links.items():
                if random.random() < chance:
                    edges.add((node, neighbor))
        return edges

    def draw_map(self, name):
        """
        Adding walls sprites of rooms and corridors to scene.sprite_list name
        :param name: a name of scene.sprite_list which contains walls
        """
        wall_list = arcade.SpriteList()  # correct!!
        coordinate_list = []
        # setup walls
        for i in range(self.room_count):
            for j in range(self.room_count):
                if self.map_matrix[i][j].exist:
                    if i + 1 < self.room_count:
                        if self.map_matrix[i + 1][j].room_id == self.map_matrix[i][j].room_id:
                            for y in range(0, self.map_matrix[i][j].height - self.map_matrix[i + 1][j].height): # right

                                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE +
                                                     self.map_matrix[i][j].width * TILE_SIZE,

                                                     (self.map_matrix[i][j].height - y) * TILE_SIZE +
                                                     j * TILE_SIZE * ROOM_SIZE)]
                        else:
                            for y in range(0, self.map_matrix[i][j].height + 1):  # right

                                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE +
                                                     self.map_matrix[i][j].width * TILE_SIZE,

                                                     y * TILE_SIZE +
                                                     j * TILE_SIZE * ROOM_SIZE)]
                    if i - 1 >= 0:
                        if self.map_matrix[i - 1][j].room_id == self.map_matrix[i][j].room_id:
                            for y in range(0, self.map_matrix[i][j].height - self.map_matrix[i - 1][j].height): # left

                                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE,

                                                     (self.map_matrix[i][j].height - y) * TILE_SIZE +
                                                     j * TILE_SIZE * ROOM_SIZE)]
                        else:
                            for y in range(0, self.map_matrix[i][j].height + 1):  # left

                                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE,

                                                     y * TILE_SIZE +
                                                     j * TILE_SIZE * ROOM_SIZE)]
                    if j + 1 < self.room_count:
                        if self.map_matrix[i][j + 1].room_id == self.map_matrix[i][j].room_id:
                            for x in range(0, self.map_matrix[i][j].width - self.map_matrix[i][j + 1].width):  # up

                                coordinate_list += [((self.map_matrix[i][j].width - x) * TILE_SIZE +
                                                     i * TILE_SIZE * ROOM_SIZE,

                                                     j * TILE_SIZE * ROOM_SIZE +
                                                     self.map_matrix[i][j].height * TILE_SIZE)]
                        else:
                            for x in range(0, self.map_matrix[i][j].width + 1):  # up

                                coordinate_list += [(x * TILE_SIZE +
                                                     i * TILE_SIZE * ROOM_SIZE,

                                                     j * TILE_SIZE * ROOM_SIZE +
                                                     self.map_matrix[i][j].height * TILE_SIZE)]
                    if j - 1 >= 0:
                        if self.map_matrix[i][j - 1].room_id == self.map_matrix[i][j].room_id:
                            for x in range(0, self.map_matrix[i][j].width - self.map_matrix[i][j - 1].width):  # down

                                coordinate_list += [((self.map_matrix[i][j].width - x) * TILE_SIZE +
                                                     i * TILE_SIZE * ROOM_SIZE,

                                                     j * TILE_SIZE * ROOM_SIZE)]
                        else:
                            for x in range(0, self.map_matrix[i][j].width + 1):  # down

                                coordinate_list += [(x * TILE_SIZE +
                                                     i * TILE_SIZE * ROOM_SIZE,

                                                     j * TILE_SIZE * ROOM_SIZE)]

        # remove tiles from corridors positions
        corridors = self.create_corridors()
        coordinate_list = set(coordinate_list) - set(corridors)

        # append walls
        append_wall_list(coordinate_list, wall_list)

        # append edges walls
        i = 0
        for j in range(self.room_count): # left (map edge)
            coordinate_list = []
            for y in range(0, self.map_matrix[i][j].height + 1):
                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE,
                                     y * TILE_SIZE + j * TILE_SIZE * ROOM_SIZE)]
            append_wall_list(coordinate_list, wall_list)

        i = self.room_count - 1
        for j in range(self.room_count): # right (map edge)
            coordinate_list = []
            for y in range(0, self.map_matrix[i][j].height + 1):
                coordinate_list += [(i * TILE_SIZE * ROOM_SIZE + self.map_matrix[i][j].width * TILE_SIZE,
                                     y * TILE_SIZE + j * TILE_SIZE * ROOM_SIZE)]
            append_wall_list(coordinate_list, wall_list)

        j = 0
        for i in range(self.room_count): # down (map edge)
            coordinate_list = []
            for x in range(0, self.map_matrix[i][j].width + 1):
                coordinate_list += [(x * TILE_SIZE + i * TILE_SIZE * ROOM_SIZE,
                                     j * TILE_SIZE * ROOM_SIZE)]
            append_wall_list(coordinate_list, wall_list)

        j = self.room_count - 1
        for i in range(self.room_count): # up (map edge)
            coordinate_list = []
            for x in range(0, self.map_matrix[i][j].width + 1):
                coordinate_list += [(x * TILE_SIZE + i * TILE_SIZE * ROOM_SIZE,
                                     j * TILE_SIZE * ROOM_SIZE + self.map_matrix[i][j].height * TILE_SIZE)]
            append_wall_list(coordinate_list, wall_list)

        # append corridors
        corridor_tiles = self.draw_corridors(corridors)
        for tile in corridor_tiles:
            wall_list.append(tile)

        # load all walls to scene
        self.scene.add_sprite_list(name, True, wall_list)

    def setup_trinket(self):
        item = arcade.Sprite(f"{PATH}sprites\\trinket.png", 0.2)
        item.center_x = ROOM_SIZE*TILE_SIZE//2
        item.center_y = ROOM_SIZE*TILE_SIZE//2
        self.trinket_sprite_list.append(item)

        self.rnd_create_trinket()
        self.rnd_create_trinket()
        self.rnd_create_trinket()
        self.rnd_create_trinket()

        self.scene.add_sprite_list("Trinket", True, self.trinket_sprite_list)
        self.trinket_amount = len(self.trinket_sprite_list)

    def rnd_create_trinket(self):
        while True:
            x = random.randint(0, self.room_count-1)
            y = random.randint(0, self.room_count-1)
            if self.map_matrix[x][y].exist:
                item = arcade.Sprite(f"{PATH}sprites\\trinket.png", 0.2)
                item.center_x = x * ROOM_SIZE * TILE_SIZE + TILE_SIZE
                item.center_y = y * ROOM_SIZE * TILE_SIZE + TILE_SIZE
                self.trinket_sprite_list.append(item)
                return

    def collect(self):
        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.person,
                                                        self.trinket_sprite_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for trinket in hit_list:
            trinket.remove_from_sprite_lists()
            self.score += 1

    def teleporting(self):
        if self.person.collides_with_sprite(self.portal):
            if self.score == self.trinket_amount:
                self.current_state = "final"
                self.is_paused = True

    def on_mouse(self):
        """
        calculate the mouse_angle relative to the player and change player facing
        """

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
        """
        move Camera to Player
        """
        # calculate camera position
        screen_x = self.person.center_x - (SCREEN_WIDTH // 2) // CAMERA_SCALING
        screen_y = self.person.center_y - (SCREEN_HEIGHT // 2) // CAMERA_SCALING

        # outboard inspection
        self.camera_x = max(min(screen_x, self.map_size - SCREEN_WIDTH // CAMERA_SCALING), 0)
        self.camera_y = max(min(screen_y, self.map_size - SCREEN_HEIGHT // CAMERA_SCALING), 0)

        # I don't know how it worked, most likely the coordinates of the vector are calculated depending on the screen
        self.camera.move_to(
            (self.camera_x * CAMERA_SCALING, self.camera_y * CAMERA_SCALING),  # vector
            min(0.1 * CAMERA_SCALING, 1)
        )

    def max_speed_check(self):
        """
        checking to avoid incorrect player speed
        """
        if self.person.correct_change_x > PLAYER_MOVEMENT_SPEED:
            self.person.correct_change_x = PLAYER_MOVEMENT_SPEED
        if self.person.correct_change_y > PLAYER_MOVEMENT_SPEED:
            self.person.correct_change_y = PLAYER_MOVEMENT_SPEED
        if self.person.correct_change_x < -PLAYER_MOVEMENT_SPEED:
            self.person.correct_change_x = -PLAYER_MOVEMENT_SPEED
        if self.person.correct_change_y < -PLAYER_MOVEMENT_SPEED:
            self.person.correct_change_y = -PLAYER_MOVEMENT_SPEED

    def on_draw(self):
        if self.current_state == "menu":
            self.start_menu.draw()
        elif self.current_state == "setup":
            self.setup()
            self.current_state = "game"
        elif self.current_state == "game":
            self.draw_game()
        elif self.current_state == "final":
            self.final_menu.draw()

    def draw_game(self):
        arcade.start_render()

        self.camera.use()

        self.draw_background()

        self.scene.draw()

        self.teleporting()
        self.portal.draw()
        arcade.draw_text(f"Score: {self.score}/{self.trinket_amount}",
                         self.portal.center_x - self.portal.width//2,
                         self.portal.center_y - self.portal.height,
                         arcade.color.WHITE, 20)

        self.pause_menu.draw()

    def on_update(self, delta_time: float):
        if self.is_paused:
            self.pause_menu.update()
            return

        self.max_speed_check()
        self.person.center_x += self.person.correct_change_x
        self.person.center_y += self.person.correct_change_y

        self.physics_engine.update()
        self.collect()

        self.on_mouse()
        self.person.update_animation(delta_time)

        self.camera_on_player()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.is_paused:
            self.pause_menu.ui_manager.on_mouse_motion(x, y, dx, dy)  # Forward mouse motion to UI Manager
        else:
            self.mouse_x = x
            self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if self.is_paused:
            self.pause_menu.ui_manager.on_mouse_press(x, y, button, modifiers)  # Forward mouse press to UI Manager
        else:
            pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.P or symbol == arcade.key.ESCAPE:  # Press 'P' to pause the game
            self.is_paused = not self.is_paused
            self.pause_menu.visible = self.is_paused

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


# Если одновременно нажать на W и S - нельзя ходить вбок, а если A и D, то движение вверх-вниз работает ? как исправить
