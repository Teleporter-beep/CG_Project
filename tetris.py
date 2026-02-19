import pygame
import random
pygame.init()
# ================= HIGH SCORE FILE =================
HIGHSCORE_FILE = "highscore.txt"
def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read())
    except:
        return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


# Screen dimensions
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
COLS = WIDTH // BLOCK_SIZE
ROWS = HEIGHT // BLOCK_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# Colors
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)

COLORS = [
    (0, 255, 255),
    (0, 0, 255),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (128, 0, 128),
    (255, 0, 0),
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
]

def create_grid():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def new_piece():
    shape = random.choice(SHAPES)
    color = COLORS[SHAPES.index(shape)]
    return {
        "shape": shape,
        "color": color,
        "x": COLS // 2 - len(shape[0]) // 2,
        "y": 0
    }

def draw_grid(grid):
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)
            if grid[y][x]:
                pygame.draw.rect(screen, grid[y][x], rect)

def valid_move(piece, grid, dx=0, dy=0):
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece["x"] + x + dx
                new_y = piece["y"] + y + dy
                if (
                    new_x < 0 or new_x >= COLS or
                    new_y >= ROWS or
                    (new_y >= 0 and grid[new_y][new_x])
                ):
                    return False
    return True

def lock_piece(piece, grid):
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                grid[piece["y"] + y][piece["x"] + x] = piece["color"]

def clear_lines(grid):
    lines_cleared = 0
    new_grid = []
    for row in grid:
        if all(row):
            lines_cleared += 1
        else:
            new_grid.append(row)

    while len(new_grid) < ROWS:
        new_grid.insert(0, [0 for _ in range(COLS)])

    return new_grid, lines_cleared

def rotate(piece, grid):
    rotated = list(zip(*piece["shape"][::-1]))
    old_shape = piece["shape"]
    piece["shape"] = rotated
    if not valid_move(piece, grid):
        piece["shape"] = old_shape

def reset_game():
    return create_grid(), new_piece(), 0, False

# Initialize game
grid, piece, score, game_over = reset_game()
highscore = load_highscore()   # <-- added
fall_time = 0
fall_speed = 500

running = True
while running:
    dt = clock.tick(60)
    fall_time += dt
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_LEFT and valid_move(piece, grid, dx=-1):
                    piece["x"] -= 1
                if event.key == pygame.K_RIGHT and valid_move(piece, grid, dx=1):
                    piece["x"] += 1
                if event.key == pygame.K_DOWN and valid_move(piece, grid, dy=1):
                    piece["y"] += 1
                if event.key == pygame.K_UP:
                    rotate(piece, grid)
            else:
                if event.key == pygame.K_r:
                    grid, piece, score, game_over = reset_game()

    if not game_over and fall_time > fall_speed:
        if valid_move(piece, grid, dy=1):
            piece["y"] += 1
        else:
            lock_piece(piece, grid)
            grid, lines = clear_lines(grid)
            score += lines * 100
            piece = new_piece()
            if not valid_move(piece, grid):
                game_over = True
                if score > highscore:          # <-- added
                    highscore = score
                    save_highscore(highscore)
        fall_time = 0

    draw_grid(grid)

    # Draw current piece
    if not game_over:
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        (piece["x"] + x) * BLOCK_SIZE,
                        (piece["y"] + y) * BLOCK_SIZE,
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    )
                    pygame.draw.rect(screen, piece["color"], rect)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Draw high score  <-- added
    highscore_text = font.render(f"High Score: {highscore}", True, WHITE)
    screen.blit(highscore_text, (10, 40))

    # Game over message
    if game_over:
        over_text = font.render("GAME OVER", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 40))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))

    pygame.display.flip()

pygame.quit()

