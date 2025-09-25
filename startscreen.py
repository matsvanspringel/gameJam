import pygame
import sys


WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)


GAME_NAME = "Veggie Vengeance"

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

    def set_text(self, text):
        self.text = text

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
    state = "menu"
    volume = 0.2
    last_nonzero_volume = volume  # onthoud laatste >0 waarde voor unmute

    # Achtergrond
    bg_raw = pygame.image.load("assets/images/RandomAssBackground.jpg").convert()
    def scale_bg():
        return pygame.transform.scale(bg_raw, (screen.get_width(), screen.get_height()))
    background_img = scale_bg()

    def start_game():
        nonlocal state
        state = "start"

    def go_settings():
        nonlocal state
        state = "settings"

    def quit_game():
        pygame.quit()
        sys.exit()

    def go_menu():
        nonlocal state
        state = "menu"

    def toggle_mute():
        nonlocal volume, last_nonzero_volume
        if volume > 0.0:
            last_nonzero_volume = volume
            volume = 0.0
        else:
            volume = last_nonzero_volume if last_nonzero_volume > 0 else 0.5

    # Menu-knoppen
    buttons = [
        Button("Start Game", 200, 50, start_game),
        Button("Settings",   200, 50, go_settings),
        Button("Quit",       200, 50, quit_game)
    ]

    # SETTINGS: slider + Mute-knop + Back-knop
    slider_width, slider_height = 240, 10
    slider_rect = pygame.Rect(0, 0, slider_width, slider_height)
    knob_x = 0
    mute_button_settings = Button("Mute", 160, 44, toggle_mute)
    back_button_settings = Button("Back to Menu", 220, 44, go_menu)

    def layout_menu():
        title = titlefont.render(GAME_NAME, True, WHITE)
        title_pos = (screen.get_width() // 2 - title.get_width() // 2, int(screen.get_height() * 0.18))

        cx = screen.get_width() // 2
        base_y = int(screen.get_height() * 0.40)
        spacing = max(60, int(screen.get_height() * 0.08))
        for i, b in enumerate(buttons):
            b.set_center(cx, base_y + i * spacing)

        return title, title_pos

    def layout_settings():
        nonlocal knob_x
        cx = screen.get_width() // 2
        h = screen.get_height()

        settings_title = titlefont.render("Settings", True, WHITE)
        settings_title_pos = (cx - settings_title.get_width() // 2, int(h * 0.18))

        # Slider centreren
        slider_rect.center = (cx, int(h * 0.45))
        knob_x = slider_rect.x + int(volume * slider_rect.width)

        # Mute-knop gecentreerd onder de slider
        mute_button_settings.set_center(cx, slider_rect.bottom + 40)
        mute_button_settings.set_text("Unmute" if volume == 0.0 else "Mute")

        # Back-knop op de locatie waar de ESC-tekst stond (onderaan)
        back_button_settings.set_center(cx, int(h * 0.85))

        small_font = pygame.font.Font(font_path, 20)
        vol_text = small_font.render(f"Volume: {int(volume*100)}%", True, WHITE)
        vol_text_pos = (cx - vol_text.get_width() // 2, mute_button_settings.rect.bottom + 12)

        # ESC-tekst verwijderd, maar ESC blijft werken via event handling
        return settings_title, settings_title_pos, vol_text, vol_text_pos

    # Initial layout
    title, title_pos = layout_menu()
    settings_title = settings_title_pos = vol_text = vol_text_pos = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                background_img = scale_bg()

            if state == "menu":
                for b in buttons:
                    b.handle_event(event)

            elif state == "settings":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if slider_rect.collidepoint(event.pos):
                        knob_x = event.pos[0]
                        volume = (knob_x - slider_rect.x) / slider_rect.width
                        volume = max(0.0, min(1.0, volume))
                if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                    if slider_rect.collidepoint(event.pos):
                        knob_x = event.pos[0]
                        volume = (knob_x - slider_rect.x) / slider_rect.width
                        volume = max(0.0, min(1.0, volume))
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    go_menu()  # ESC blijft de functie behouden

                mute_button_settings.handle_event(event)
                back_button_settings.handle_event(event)

        # Elke frame layout updaten (responsive)
        background_img = pygame.transform.scale(bg_raw, (screen.get_width(), screen.get_height()))
        title, title_pos = layout_menu()
        if state == "settings":
            settings_title, settings_title_pos, vol_text, vol_text_pos = layout_settings()

        screen.blit(background_img, (0, 0))

        if state == "menu":
            screen.blit(title, title_pos)
            for b in buttons:
                b.draw(screen)

        elif state == "settings":
            screen.blit(settings_title, settings_title_pos)
            pygame.draw.rect(screen, GRAY, slider_rect, border_radius=5)
            knob_x = max(slider_rect.x, min(knob_x, slider_rect.x + slider_rect.width))
            pygame.draw.circle(screen, WHITE, (knob_x, slider_rect.centery), 12)

            mute_button_settings.draw(screen)
            back_button_settings.draw(screen)
            screen.blit(vol_text, vol_text_pos)

        pygame.display.flip()
        clock.tick(60)

        pygame.mixer.music.set_volume(volume)

        if state == "start":
            return volume
