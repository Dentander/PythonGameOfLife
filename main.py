import pygame as pg
from config import *
import random


# n - neighboring
def get_n_cells(pos):
    px, py = pos
    return [
        (px + 1, py + 1),
        (px - 1, py + 1),
        (px + 1, py - 1),
        (px - 1, py - 1),
        (px, py + 1),
        (px, py - 1),
        (px + 1, py),
        (px - 1, py)
    ]


class User:
    def __init__(self):
        self.indent_x, self.indent_y = 0, 0
        self.pmx, self.pmy = False, False
        self.speed = MOVE_SPEED
        self.tile = DEF_TILE
        self.chosen_cell = 0, 0

    def int_tile(self):
        return int(self.tile)

    def get_indent(self):
        return self.indent_x, self.indent_y

    def tile_change(self, button):
        mouse_x, mouse_y = pg.mouse.get_pos()
        dist_x, dist_y = mouse_x - self.indent_x, mouse_y - self.indent_y
        new_tile = self.tile
        if button == 4 and self.tile + self.tile / DEF_TILE <= MAX_TILE:
            new_tile += self.tile / DEF_TILE
        if button == 5 and self.tile - self.tile / DEF_TILE >= MIN_TILE:
            new_tile -= self.tile / DEF_TILE
        self.indent_x += dist_x - dist_x * new_tile / self.tile
        self.indent_y += dist_y - dist_y * new_tile / self.tile
        self.tile = new_tile

        if self.tile > MAX_TILE:
            self.tile = MAX_TILE
        if self.tile < MIN_TILE:
            self.tile = MIN_TILE

    def mouse_update(self):
        mouse = pg.mouse.get_pressed()
        if mouse[2] and self.pmx and self.pmy:
            amx, amy = pg.mouse.get_pos()
            self.indent_x += (amx - self.pmx)
            self.indent_y += (amy - self.pmy)
            self.pmx, self.pmy = amx, amy
        elif mouse[2]:
            self.pmx, self.pmy = pg.mouse.get_pos()
        else:
            self.pmx, self.pmy = False, False

    def keys_update(self, delta_time):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.indent_y += self.speed * delta_time * self.tile
        if keys[pg.K_s]:
            self.indent_y -= self.speed * delta_time * self.tile
        if keys[pg.K_a]:
            self.indent_x += self.speed * delta_time * self.tile
        if keys[pg.K_d]:
            self.indent_x -= self.speed * delta_time * self.tile

    def chosen_cell_update(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        dist_x, dist_y = mouse_x - self.indent_x, mouse_y - self.indent_y
        self.chosen_cell = dist_x // self.tile, dist_y // self.tile

    def update(self, delta_time):
        self.mouse_update()
        self.keys_update(delta_time)
        self.chosen_cell_update()


class CellularAutomaton:
    def __init__(self):
        self.delta_time = 0
        self.cells = set()
        self.random_restart(0.2)

    def random_restart(self, filling_ratio, tile=DEF_TILE):
        for _ in range(int(WIDTH * HEIGHT / tile / tile * filling_ratio)):
            pos = (random.randint(0, WIDTH // tile), random.randint(0, HEIGHT // tile))
            self.cells.add(pos)

    def update(self, delta_time):
        if SYNCHRONIZATION:
            self.delta_time += delta_time
            if self.delta_time > TIME_BETWEEN_RENDERERS:
                self.delta_time %= TIME_BETWEEN_RENDERERS
                self.render()
        else:
            self.render()

    def count_n_cells(self, cell):
        res = 0
        for i in get_n_cells(cell):
            if i in self.cells:
                res += 1
        return res

    def render(self):
        future_cells = set()
        for cell in self.cells:
            # self render
            if cell not in future_cells and 2 <= self.count_n_cells(cell) <= 3:
                future_cells.add(cell)

            # n cells render
            for n_cell in get_n_cells(cell):
                if n_cell not in future_cells and self.count_n_cells(n_cell) == 3:
                    future_cells.add(n_cell)
        self.cells = future_cells

    def draw(self, sc, user):
        indent_x, indent_y = user.get_indent()
        tile = user.tile
        [pg.draw.rect(sc, BLACK,
                      (cell[0] * tile + indent_x, cell[1] * tile + indent_y, tile + 1, tile + 1))
         for cell in self.cells]
        chosen_cell_color = BLACK
        if user.chosen_cell in self.cells:
            chosen_cell_color = SKY_BLUE
        chosen_cell_x, chosen_cell_y = user.chosen_cell
        pg.draw.rect(sc, chosen_cell_color,
                     (chosen_cell_x * tile + indent_x, chosen_cell_y * tile + indent_y, tile, tile), 2)


class App:
    def __init__(self):
        self.screen = pg.display.set_mode(RESOLUTION, pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.end_app = False

        self.user = User()
        self.ca = CellularAutomaton()

    def run(self):
        while not self.end_app:
            self.screen.fill(SKY_BLUE)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.user.tile_change(event.button)

            self.user.update(self.clock.get_time())
            self.ca.update(self.clock.get_time())
            self.ca.draw(self.screen, self.user)

            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    app = App()
    app.run()
