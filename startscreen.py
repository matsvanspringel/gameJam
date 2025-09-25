import pygame
import sys

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.font = pygame.font.SysFont("arial", 30)

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


def show_start_screen(screen):
    clock = pygame.time.Clock()
    state = "menu"   # "menu" of "settings"
    volume = 0.5     # begin volume

    background_img = pygame.image.load("assets/images/RandomAssBackground.jpg").convert()
    background_img = pygame.transform.scale(background_img, (screen.get_width(), screen.get_height()))



    # functies die de knoppen gebruiken
    def start_game():
        nonlocal state
        state = "start"

    def go_settings():
        nonlocal state
        state = "settings"

    def quit_game():
        pygame.quit()
        sys.exit()

    # --- knoppen ---
    buttons = [
        Button("Start Game", screen.get_width()//2 - 100, 200, 200, 50, start_game),
        Button("Settings",  screen.get_width()//2 - 100, 300, 200, 50, go_settings),
        Button("Quit",      screen.get_width()//2 - 100, 400, 200, 50, quit_game)
    ]

    font = pygame.font.SysFont("arial", 40)

    # --- settings slider ---
    slider_rect = pygame.Rect(screen.get_width()//2 - 100, 300, 200, 10)
    knob_x = slider_rect.x + int(volume * slider_rect.width)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            screen.blit(background_img, (0, 0))

            if state == "menu":
                for b in buttons:
                    b.handle_event(event)



            elif state == "settings":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if slider_rect.collidepoint(event.pos):
                        knob_x = event.pos[0]
                        volume = (knob_x - slider_rect.x) / slider_rect.width
                if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                    if slider_rect.collidepoint(event.pos):
                        knob_x = event.pos[0]
                        volume = (knob_x - slider_rect.x) / slider_rect.width
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "menu"



        if state == "menu":
            title = font.render("Vampire Survivors Clone", True, WHITE)
            screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
            for b in buttons:
                b.draw(screen)

        elif state == "settings":
            title = font.render("Settings", True, WHITE)
            screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))

            # slider tekenen
            pygame.draw.rect(screen, GRAY, slider_rect)
            knob_x = max(slider_rect.x, min(knob_x, slider_rect.x + slider_rect.width))
            pygame.draw.circle(screen, WHITE, (knob_x, slider_rect.centery), 12)

            vol_text = font.render(f"Volume: {int(volume*100)}%", True, WHITE)
            screen.blit(vol_text, (screen.get_width()//2 - vol_text.get_width()//2, 350))

            esc_text = pygame.font.SysFont("arial", 20).render("Druk ESC om terug te keren", True, WHITE)
            screen.blit(esc_text, (screen.get_width()//2 - esc_text.get_width()//2, 500))

        pygame.display.flip()
        clock.tick(60)

        if state == "start":
            return volume  # geef volume terug
