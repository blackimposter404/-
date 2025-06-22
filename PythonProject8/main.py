import pygame as pg
import pygame_menu
import random
import sys
import json
import os

pg.init()

CELL_SIZE = 40
MARGIN = 2
PANEL_HEIGHT = 50

DIFFICULTIES = {
    'easy': {'rows': 9, 'cols': 9, 'mines': 10},
    'medium': {'rows': 16, 'cols': 16, 'mines': 40},
    'hard': {'rows': 16, 'cols': 30, 'mines': 99}
}

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (155, 155, 155)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
COLORS = [
    None, BLUE, GREEN, RED, (0, 0, 128), (128, 0, 0),
    (0, 128, 128), BLACK, DARK_GRAY
]

font = pg.font.SysFont('Arial', 20)
large_font = pg.font.SysFont('Arial', 40)

HIGH_SCORE_FILE = 'highscores.json'

if os.path.exists(HIGH_SCORE_FILE):
    with open(HIGH_SCORE_FILE, 'r') as f:
        high_scores = json.load(f)
else:
    high_scores = {'easy': 999, 'medium': 999, 'hard': 999}

class Minesweeper:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flagged = [[False for _ in range(cols)] for _ in range(rows)]
        self.game_over = False
        self.win = False
        self.first_click = True
        self.bombs_left = mines
        self.start_time = None
        self.elapsed_time = 0

        self.SCREEN_WIDTH = self.cols * (CELL_SIZE + MARGIN) + MARGIN
        self.SCREEN_HEIGHT = PANEL_HEIGHT + self.rows * (CELL_SIZE + MARGIN) + MARGIN
        self.screen = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pg.display.set_caption('Сапёр')
        icon = pg.image.load('Bomb.png')
        pg.display.set_icon(icon)

        self.button_rect = pg.Rect(self.SCREEN_WIDTH - 110, 10, 100, 30)

    def place_bombs(self, first_click_row, first_click_col):
        bombs_placed = 0
        while bombs_placed < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row != first_click_row or col != first_click_col) and self.grid[row][col] != -1:
                self.grid[row][col] = -1
                bombs_placed += 1
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != -1:
                    self.grid[row][col] = self.count_adjacent_bombs(row, col)

    def count_adjacent_bombs(self, row, col):
        count = 0
        for r in range(max(0, row - 1), min(self.rows, row + 2)):
            for c in range(max(0, col - 1), min(self.cols, col + 2)):
                if self.grid[r][c] == -1:
                    count += 1
        return count

    def reveal(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        if self.revealed[row][col] or self.flagged[row][col] or self.game_over:
            return
        self.revealed[row][col] = True
        if self.first_click:
            self.place_bombs(row, col)
            self.first_click = False
            self.start_time = pg.time.get_ticks()
        if self.grid[row][col] == -1:
            self.game_over = True
            self.reveal_all_bombs()
            return
        if self.grid[row][col] == 0:
            for r in range(max(0, row - 1), min(self.rows, row + 2)):
                for c in range(max(0, col - 1), min(self.cols, col + 2)):
                    if not (r == row and c == col):
                        self.reveal(r, c)
        self.check_win()

    def reveal_all_bombs(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == -1:
                    self.revealed[row][col] = True

    def toggle_flag(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        if self.revealed[row][col] or self.game_over:
            return
        self.flagged[row][col] = not self.flagged[row][col]
        if self.flagged[row][col]:
            self.bombs_left -= 1
        else:
            self.bombs_left += 1
        self.check_win()

    def check_win(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != -1 and not self.revealed[row][col]:
                    return
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == -1 and not self.flagged[row][col]:
                    return
        self.game_over = True
        self.win = True
        self.reveal_all_bombs()
        self.elapsed_time = (pg.time.get_ticks() - self.start_time) // 1000
        difficulty = self.get_difficulty()
        if difficulty in high_scores and self.elapsed_time < high_scores[difficulty]:
            high_scores[difficulty] = self.elapsed_time
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(high_scores, f)

    def get_difficulty(self):
        if self.rows == 9 and self.cols == 9 and self.mines == 10:
            return 'easy'
        elif self.rows == 16 and self.cols == 16 and self.mines == 40:
            return 'medium'
        elif self.rows == 16 and self.cols == 30 and self.mines == 99:
            return 'hard'
        else:
            return 'custom'

    def draw(self):
        self.screen.fill(WHITE)
        pg.draw.rect(self.screen, GRAY, (0, 0, self.SCREEN_WIDTH, PANEL_HEIGHT))
        if self.start_time and not self.game_over:
            self.elapsed_time = (pg.time.get_ticks() - self.start_time) // 1000
        timer_text = font.render(f"Время: {self.elapsed_time} сек", True, BLACK)
        self.screen.blit(timer_text, (10, 10))
        mines_text = font.render(f"Мин осталось: {self.bombs_left}", True, BLACK)
        self.screen.blit(mines_text, (self.SCREEN_WIDTH // 2 - 50, 10))
        pg.draw.rect(self.screen, DARK_GRAY, self.button_rect)
        button_text = font.render("Новая игра", True, BLACK)
        self.screen.blit(button_text, (self.button_rect.x + 10, self.button_rect.y + 5))
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pg.Rect(
                    MARGIN + col * (CELL_SIZE + MARGIN),
                    PANEL_HEIGHT + MARGIN + row * (CELL_SIZE + MARGIN),
                    CELL_SIZE,
                    CELL_SIZE
                )
                if self.revealed[row][col]:
                    pg.draw.rect(self.screen, DARK_GRAY, rect)
                    pg.draw.rect(self.screen, BLACK, rect, 1)
                    if self.grid[row][col] == -1:
                        pg.draw.circle(self.screen, BLACK, rect.center, CELL_SIZE // 3)
                    elif self.grid[row][col] > 0:
                        text = font.render(str(self.grid[row][col]), True, COLORS[self.grid[row][col]])
                        text_rect = text.get_rect(center=rect.center)
                        self.screen.blit(text, text_rect)
                else:
                    pg.draw.rect(self.screen, GRAY, rect)
                    pg.draw.rect(self.screen, BLACK, rect, 1)
                    if self.flagged[row][col]:
                        pg.draw.polygon(self.screen, RED, [
                            (rect.left + 5, rect.bottom - 5),
                            (rect.left + 5, rect.top + 5),
                            (rect.right - 5, rect.top + CELL_SIZE // 2)
                        ])

def main(rows, cols, mines):
    game = Minesweeper(rows, cols, mines)
    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                if game.button_rect.collidepoint(pos):
                    pg.display.set_mode((400, 400))
                    main(rows, cols, mines)
                    return
                else:
                    if (MARGIN <= pos[0] < MARGIN + game.cols * (CELL_SIZE + MARGIN) and
                            PANEL_HEIGHT + MARGIN <= pos[1] < PANEL_HEIGHT + MARGIN + game.rows * (CELL_SIZE + MARGIN)):
                        col = (pos[0] - MARGIN) // (CELL_SIZE + MARGIN)
                        row = (pos[1] - PANEL_HEIGHT - MARGIN) // (CELL_SIZE + MARGIN)
                        if event.button == 1:
                            game.reveal(row, col)
                        elif event.button == 3:
                            game.toggle_flag(row, col)
        game.draw()
        if game.game_over:
            pg.display.flip()
            pg.time.wait(1000)
            pg.display.set_mode((400, 400))
            if game.win:
                show_win_screen(game)
            else:
                show_end_screen()
            running = False
        pg.display.flip()
        clock.tick(30)
    pg.quit()
    sys.exit()

def show_end_screen():
    end_menu = pygame_menu.Menu('БААААААМ!', 380, 380, theme=pygame_menu.themes.THEME_DARK)
    end_menu.add.button('Новая игра', show_start_screen)
    end_menu.add.button('Выйти', pygame_menu.events.EXIT)
    end_menu.mainloop(pg.display.get_surface())

def show_win_screen(game):
    difficulty = game.get_difficulty()
    high_score = high_scores.get(difficulty, 999)
    win_menu = pygame_menu.Menu('Ну ты и сапёр!', 380, 380, theme=pygame_menu.themes.THEME_GREEN)
    win_menu.add.label(f"Ваше время: {game.elapsed_time} сек")
    win_menu.add.label(f"Лучшее время: {high_score} сек")
    win_menu.add.button('Новая игра', show_start_screen)
    win_menu.add.button('Выйти', pygame_menu.events.EXIT)
    win_menu.mainloop(pg.display.get_surface())

def closures():
    pg.quit()
    sys.exit()

def show_start_screen():
    menu = pygame_menu.Menu('Сапёр', 380, 380, theme=pygame_menu.themes.THEME_ORANGE)
    menu.add.button('Легко', lambda: main(9, 9, 10))
    menu.add.button('Средне', lambda: main(16, 16, 40))
    menu.add.button('Сложно', lambda: main(16, 30, 99))
    menu.add.button('Выйти', closures)
    menu.mainloop(pg.display.get_surface())

if __name__ == '__main__':
    pg.display.set_mode((400, 400))
    show_start_screen()