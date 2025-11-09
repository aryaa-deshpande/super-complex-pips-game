
import arcade

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Domino Game"


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        # Sprites for images
        self.domino_sprite = None
        self.play_sprite = None
        self.statistics_sprite = None
        self.settings_sprite = None
        self.quit_sprite = None

        # Button positions (bottom left corner, stacked vertically)
        self.button_left_margin = 15
        self.button_spacing = 30
        self.button_start_y = 150
        self.target_button_width = 200  # for consistent scaling

    def setup(self):
        """Load all the images as sprites"""
        path = "super-complex-pips-game/"
        try:
            # Create sprites from image files
            self.domino_sprite = arcade.Sprite("/Users/aryaapareshdeshpande/Desktop/Aryaa/Hackathon/super-complex-pips-game/frontend/menu/domino.png")
            self.domino_sprite.center_x = SCREEN_WIDTH // 2
            self.domino_sprite.center_y = SCREEN_HEIGHT // 2

            # Button sprites
            self.play_sprite = arcade.Sprite("/Users/aryaapareshdeshpande/Desktop/Aryaa/Hackathon/super-complex-pips-game/frontend/menu/play.png")
            self.play_sprite.scale = 0.25
            self.play_sprite.left = 15
            self.play_sprite.center_y = self.button_start_y

            self.statistics_sprite = arcade.Sprite("/Users/aryaapareshdeshpande/Desktop/Aryaa/Hackathon/super-complex-pips-game/frontend/menu/statistics.png")
            self.statistics_sprite.scale = 0.20
            self.statistics_sprite.left = 24
            self.statistics_sprite.center_y = self.button_start_y - 40

            self.settings_sprite = arcade.Sprite("/Users/aryaapareshdeshpande/Desktop/Aryaa/Hackathon/super-complex-pips-game/frontend/menu/settings.png")
            self.settings_sprite.scale = 0.186
            self.settings_sprite.left = 24
            self.settings_sprite.center_y = self.button_start_y - 60

            self.quit_sprite = arcade.Sprite("/Users/aryaapareshdeshpande/Desktop/Aryaa/Hackathon/super-complex-pips-game/frontend/menu/quit.png")
            self.quit_sprite.scale = 0.12
            self.quit_sprite.left = 22
            self.quit_sprite.center_y = self.button_start_y - 80

            print("All images loaded successfully!")

        except Exception as e:
            print(f"Error loading images: {e}")

    def on_draw(self):
        """Render the screen"""
        # 2.6 uses start_render() instead of clear()
        arcade.start_render()
        arcade.set_background_color(arcade.color.BLACK)

        # Draw all sprites (2.6 syntax)
        if self.domino_sprite:
            self.domino_sprite.draw()

        if self.play_sprite:
            self.play_sprite.draw()

        if self.statistics_sprite:
            self.statistics_sprite.draw()

        if self.settings_sprite:
            self.settings_sprite.draw()

        if self.quit_sprite:
            self.quit_sprite.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks on buttons"""
        # Define approximate click bounds for each button
        play_bounds = (15, 115, 135, 165)
        stats_bounds = (24, 154, 95, 125)
        settings_bounds = (24, 139, 75, 105)
        quit_bounds = (22, 77, 55, 80)

        if quit_bounds[0] <= x <= quit_bounds[1] and quit_bounds[2] <= y <= quit_bounds[3]:
            print("Quit button clicked - Closing game...")
            arcade.close_window()

        elif settings_bounds[0] <= x <= settings_bounds[1] and settings_bounds[2] <= y <= settings_bounds[3]:
            print("Settings button clicked")

        elif stats_bounds[0] <= x <= stats_bounds[1] and stats_bounds[2] <= y <= stats_bounds[3]:
            print("Statistics button clicked")

        elif play_bounds[0] <= x <= play_bounds[1] and play_bounds[2] <= y <= play_bounds[3]:
            print("Play button clicked - Starting game...")
            # TODO: Switch to game view


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MenuView()
    menu_view.setup()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()

