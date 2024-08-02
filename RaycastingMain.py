import pygame, sys, math, time, re, string, os

TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

MAP = (
    '########'
    '# #    #'
    '# # #  #'
    '#      #'
    '#   #  #'
    '#  #   #'
    '#   #  #'
    '########'
)

class game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.rel = 0
        self.FPS = 0
        self.clock = pygame.time.Clock()
        self.SCREEN_HEIGHT = 1020
        self.SCREEN_WIDTH = 1920
        self.WIDTH = self.SCREEN_WIDTH
        self.HEIGHT = self.SCREEN_HEIGHT
        self.res = self.SCREEN_WIDTH, self.SCREEN_HEIGHT
        self.MAP_SIZE = 8
        self.TILE_SIZE = int((self.SCREEN_WIDTH / 2) / self.MAP_SIZE)
        self.MAX_DEPTH = 1000
        self.FOV = math.pi / 3  # Use floating-point division
        self.HALF_FOV = self.FOV / 2
        self.CASTED_RAYS = 120
        self.STEP_ANGLE = self.FOV / self.CASTED_RAYS
        self.SCALE = self.SCREEN_WIDTH // self.CASTED_RAYS
        self.HALF_WIDTH = self.SCREEN_WIDTH // 2
        self.HALF_HEIGHT = self.SCREEN_HEIGHT // 2
        self.MOUSE_SENSITIVITY = 0.0001
        self.MOUSE_MAX_REL = 40
        self.MOUSE_BORDER_LEFT = 1600
        self.MOUSE_BORDER_RIGHT = self.SCREEN_WIDTH - self.MOUSE_BORDER_LEFT
        self.player_x = (self.SCREEN_WIDTH / 2) / 2
        self.player_y = (self.SCREEN_WIDTH / 2) / 2
        self.player_angle = math.pi
        self.screen = pygame.display.set_mode(self.res)
        self.delta_time = 1
        self.forward = True
        self.PLAYER_MAX_HEALTH = 250
        self.player_health = self.PLAYER_MAX_HEALTH
        self.new_game()

    def new_game(self):
        self.object_renderer = ObjectRenderer(self)
        self.run()

    def run(self):
        self.forward = True
        while True:
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_w]:
            self.forward = True
            self.player_x += -math.sin(self.player_angle) * 2
            self.player_y += math.cos(self.player_angle) * 2
        if self.keys[pygame.K_s]:
            self.forward = False
            self.player_x -= -math.sin(self.player_angle) * 2
            self.player_y -= math.cos(self.player_angle) * 2
        if self.keys[pygame.K_a]:
            self.player_angle -= 0.1
        if self.keys[pygame.K_d]:
            self.player_angle += 0.1

        self.col = int(self.player_x / self.TILE_SIZE)
        self.row = int(self.player_y / self.TILE_SIZE)
        self.square = self.row * self.MAP_SIZE + self.col

        if MAP[self.square] == '#':
            if self.forward:
                self.player_x -= -math.sin(self.player_angle) * 2
                self.player_y -= math.cos(self.player_angle) * 2
            else:
                self.player_x += -math.sin(self.player_angle) * 2
                self.player_y += math.cos(self.player_angle) * 2

        mx, my = pygame.mouse.get_pos()
        if mx < self.MOUSE_BORDER_LEFT or mx > self.MOUSE_BORDER_RIGHT:
            pygame.mouse.set_pos([self.HALF_WIDTH, self.HALF_HEIGHT])
        self.rel = pygame.mouse.get_rel()[0]
        self.rel = max(-self.MOUSE_MAX_REL, min(self.MOUSE_MAX_REL, self.rel))
        self.player_angle += self.rel * self.MOUSE_SENSITIVITY * self.delta_time

    def draw(self):
        self.object_renderer.draw()

    def update(self):
        pygame.display.set_caption(f'Raycasting Game Engine By Rylan / Frames: {self.clock.get_fps() :.1f}')
        self.object_renderer.cast_rays()
        pygame.display.flip()
        self.delta_time = self.clock.tick(self.FPS)

class ObjectRenderer():
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.FLOOR_COLOUR = 50, 50, 50

    def draw_map(self):
        for row in range(8):
            for col in range(8):
                square = row * self.game.MAP_SIZE + col
                pygame.draw.rect(
                    self.screen,
                    (200, 200, 200) if MAP[square] == '#' else (100, 100, 100),
                    (col * self.game.TILE_SIZE, row * self.game.TILE_SIZE, self.game.TILE_SIZE - 2, self.game.TILE_SIZE - 2)
                )
        pygame.draw.circle(self.screen, (255, 0, 0), (int(self.game.player_x), int(self.game.player_y)), 8)
        pygame.draw.line(self.screen, (0, 255, 0), (self.game.player_x, self.game.player_y),
                         (self.game.player_x - math.sin(self.game.player_angle) * 50,
                          self.game.player_y + math.cos(self.game.player_angle) * 50), 3)
        pygame.draw.line(self.screen, (0, 255, 0), (self.game.player_x, self.game.player_y),
                         (self.game.player_x - math.sin(self.game.player_angle - self.game.HALF_FOV) * 50,
                          self.game.player_y + math.cos(self.game.player_angle - self.game.HALF_FOV) * 50), 3)
        pygame.draw.line(self.screen, (0, 255, 0), (self.game.player_x, self.game.player_y),
                         (self.game.player_x - math.sin(self.game.player_angle + self.game.HALF_FOV) * 50,
                          self.game.player_y + math.cos(self.game.player_angle + self.game.HALF_FOV) * 50), 3)

    def draw(self):
        self.draw_background()
        # self.draw_map()

    def draw_background(self):
        self.WIDTH = self.game.WIDTH
        self.HEIGHT = self.game.HEIGHT
        self.HALF_HEIGHT = self.game.HALF_HEIGHT
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, self.FLOOR_COLOUR, (0, self.HALF_HEIGHT, self.WIDTH, self.HEIGHT))

    def cast_rays(self):
        start_angle = self.game.player_angle - self.game.HALF_FOV
        for ray in range(self.game.CASTED_RAYS):
            for depth in range(self.game.MAX_DEPTH):
                target_x = self.game.player_x - math.sin(start_angle) * depth
                target_y = self.game.player_y + math.cos(start_angle) * depth
                col = int(target_x / self.game.TILE_SIZE)
                row = int(target_y / self.game.TILE_SIZE)
                square = row * self.game.MAP_SIZE + col

                if MAP[square] == '#':
                    color = 255 / (1 + depth * depth * depth * 0.0001)
                    depth *= math.cos(self.game.player_angle - start_angle)
                    self.wall_height = (self.game.TILE_SIZE * self.game.SCREEN_HEIGHT) / (depth + 0.0001)

                    if self.wall_height > self.game.SCREEN_HEIGHT:
                        self.wall_height = self.game.SCREEN_HEIGHT

                    screen_x = ray * self.game.SCALE
                    wall_start_y = (self.game.SCREEN_HEIGHT / 2) - (self.wall_height / 2)
                    pygame.draw.rect(self.screen, (color, color, color), (screen_x, wall_start_y, self.game.SCALE, self.wall_height))
                    break

            start_angle += self.game.STEP_ANGLE

if __name__ == '__main__':
    game = game()
    game.run()
