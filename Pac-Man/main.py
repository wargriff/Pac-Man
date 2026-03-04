import pygame
from script.game_play import Game

pygame.init()

# ==============================
# WINDOW CONFIG
# ==============================
START_WIDTH = 900
START_HEIGHT = 700

screen = pygame.display.set_mode(
    (START_WIDTH, START_HEIGHT),
    pygame.RESIZABLE
)

pygame.display.set_caption("Pac-Man Python")
clock = pygame.time.Clock()

# ==============================
# STATES
# ==============================
MENU = "menu"
GAME = "game"
GAME_OVER = "game_over"
WIN = "win"

state = MENU

# ==============================
# GAME INSTANCE
# ==============================
game = Game(screen)

font_big = pygame.font.SysFont("Arial", 70, bold=True)
font_small = pygame.font.SysFont("Arial", 32)

running = True

# ==============================
# MAIN LOOP
# ==============================
while running:

    clock.tick(60)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:

            screen = pygame.display.set_mode(
                (event.w, event.h),
                pygame.RESIZABLE
            )

            game.resize(event.w, event.h)

        elif event.type == pygame.KEYDOWN:

            if state == MENU and event.key == pygame.K_RETURN:
                game.reset_full_game()
                state = GAME

            elif state in (GAME_OVER, WIN) and event.key == pygame.K_r:
                state = MENU

    # ---------------- UPDATE ----------------
    if state == GAME:

        game.update()

        if game.lives <= 0:
            state = GAME_OVER

        # condition de victoire plus logique
        if game.level >= 10:
            state = WIN

    # ---------------- DRAW ----------------
    screen.fill((10, 10, 25))

    width = screen.get_width()
    height = screen.get_height()

    center_x = width // 2

    if state == MENU:

        title = font_big.render("PAC-MAN", True, (255, 255, 0))
        start_text = font_small.render(
            "Appuie sur ENTREE pour jouer",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (center_x - title.get_width() // 2, int(height * 0.3))
        )

        screen.blit(
            start_text,
            (center_x - start_text.get_width() // 2, int(height * 0.45))
        )

    elif state == GAME:

        game.draw()

    elif state == GAME_OVER:

        over_text = font_big.render("GAME OVER", True, (255, 0, 0))
        retry_text = font_small.render(
            "Appuie sur R pour retourner au menu",
            True,
            (255, 255, 255)
        )

        screen.blit(
            over_text,
            (center_x - over_text.get_width() // 2, int(height * 0.35))
        )

        screen.blit(
            retry_text,
            (center_x - retry_text.get_width() // 2, int(height * 0.5))
        )

    elif state == WIN:

        win_text = font_big.render("VICTOIRE !", True, (0, 255, 0))
        retry_text = font_small.render(
            "Appuie sur R pour retourner au menu",
            True,
            (255, 255, 255)
        )

        screen.blit(
            win_text,
            (center_x - win_text.get_width() // 2, int(height * 0.35))
        )

        screen.blit(
            retry_text,
            (center_x - retry_text.get_width() // 2, int(height * 0.5))
        )

    pygame.display.flip()

pygame.quit()