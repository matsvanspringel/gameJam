import pygame
import sys

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

GAME_NAME = "Paused"

pygame.init()

font_title_path = "assets/fonts/PressStart2P-Regular.ttf"
titlefont = pygame.font.Font(font_title_path, 40)
font_path = "assets/fonts/PixelifySans-VariableFont_wght.ttf"
font = pygame.font.Font(font_path, 30)

class Button:
    def __init__(self, text, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(0, 0, width, height)
        self.callback = callback
        self.font = font

    def set_center(self, x, y):
        self.rect.center = (x, y)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = GRAY if self.rect.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, WHITE)
        screen.blit(text_surf, (
            self.rect.centerx - text_surf.get_width() // 2,
            self.rect.centery - text_surf.get_height() // 2
        ))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

def show_pause_screen(screen):
    clock = pygame.time.Clock()
    result = None  # "resume" | "main_menu" | "quit"


    bg_raw = pygame.image.load("assets/images/RandomAssBackground.jpg").convert()
    def scale_bg():
        return pygame.transform.scale(bg_raw, (screen.get_width(), screen.get_height()))
    background_img = scale_bg()

    # Callbacks for buttons
    def do_resume():
        nonlocal result
        result = "resume"

    def go_main_menu():
        nonlocal result
        result = "main_menu"

    def do_quit():
        nonlocal result
        result = "quit"

    # BUTTONS
    buttons = [
        Button("Resume",     200, 50, do_resume),
        Button("Main Menu",  200, 50, go_main_menu),
        Button("Quit Game",  200, 50, do_quit),
    ]

    def layout_menu():
        title = titlefont.render(GAME_NAME, True, WHITE)
        title_pos = (screen.get_width() // 2 - title.get_width() // 2, int(screen.get_height() * 0.18))

        cx = screen.get_width() // 2
        base_y = int(screen.get_height() * 0.40)
        spacing = max(60, int(screen.get_height() * 0.08))
        for i, b in enumerate(buttons):
            b.set_center(cx, base_y + i * spacing)

        return title, title_pos

    title, title_pos = layout_menu()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.VIDEORESIZE:
                background_img = scale_bg()
                title, title_pos = layout_menu()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "resume"  # ESC resumes the game

            for b in buttons:
                b.handle_event(event)

        if result is not None:
            return result

        # Responsive redraw
        background_img = pygame.transform.scale(bg_raw, (screen.get_width(), screen.get_height()))
        title, title_pos = layout_menu()

        screen.blit(background_img, (0, 0))
        screen.blit(title, title_pos)
        for b in buttons:
            b.draw(screen)

        pygame.display.flip()
        clock.tick(60)
