import pygame
from script.game_play import Game
from script.menu import Menu, GameOverUI

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
# INSTANCES
# ==============================
game = Game(screen)
menu = Menu(screen)
game_over_ui = GameOverUI(screen)

# Fonts pour WIN (créées UNE seule fois)
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

            game.screen = screen
            menu.screen = screen
            game_over_ui.screen = screen

        elif event.type == pygame.KEYDOWN:

            if state == MENU and event.key == pygame.K_RETURN:
                game.reset_full_game()
                state = GAME

        # 👇 Gestion bouton Game Over
        if state == GAME_OVER:
            if game_over_ui.handle_event(event):
                game.restart_game()
                state = MENU

    # ---------------- UPDATE ----------------
    if state == GAME:

        game.update()

        # ✅ CORRECTION ICI
        if game.game_over:
            state = GAME_OVER

        if game.level >= 10:
            state = WIN

    # ---------------- DRAW ----------------
    screen.fill((10, 10, 25))

    if state == MENU:
        menu.draw()

    elif state == GAME:
        game.draw()

    elif state == GAME_OVER:
        game.draw()
        game_over_ui.draw()

    elif state == WIN:
        game.draw()

        width = screen.get_width()
        height = screen.get_height()
        center_x = width // 2
        center_y = height // 2

        overlay = pygame.Surface((width, height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        win_text = font_big.render("VICTOIRE !", True, (0, 255, 0))
        retry_text = font_small.render(
            "Clique sur Restart pour rejouer",
            True,
            (255, 255, 255)
        )

        screen.blit(
            win_text,
            (center_x - win_text.get_width() // 2, center_y - 100)
        )

        screen.blit(
            retry_text,
            (center_x - retry_text.get_width() // 2, center_y)
        )

    pygame.display.flip()

pygame.quit()