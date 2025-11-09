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
        self.button_left_margin = 15  # Distance from left edge
        self.button_spacing = 30  # Spacing between buttons
        self.button_start_y = 150
        self.target_button_width = 200  # Target width for all buttons (keeps aspect ratio better)
        
    def setup(self):
        """Load all the images as sprites"""
        path = "anaconda-ubuntu/shared_folder/super-complex-pips-game/"
        try:
            # Create sprites from image files
            self.domino_sprite = arcade.Sprite(path + "assets/menu/domino_character.png")
            self.domino_sprite.center_x = SCREEN_WIDTH // 2
            self.domino_sprite.center_y = SCREEN_HEIGHT // 2
            
            # Create button sprites and scale them to the same width
            self.play_sprite = arcade.Sprite(path + "assets/menu/play.png")
            scale = self.target_button_width / self.play_sprite.width
            self.play_sprite.scale = .25
            self.play_sprite.left = 15
            self.play_sprite.center_y = self.button_start_y
            
            self.statistics_sprite = arcade.Sprite(path + "assets/menu/statistics.png")
            scale = self.target_button_width / self.statistics_sprite.width
            self.statistics_sprite.scale = .2
            self.statistics_sprite.left = 24
            self.statistics_sprite.center_y = self.button_start_y - 40
            
            self.settings_sprite = arcade.Sprite(path + "assets/menu/settings.png")
            scale = self.target_button_width / self.settings_sprite.width
            self.settings_sprite.scale = .186
            self.settings_sprite.left = 24
            self.settings_sprite.center_y = self.button_start_y - 60
            
            self.quit_sprite = arcade.Sprite(path + "assets/menu/quit.png")
            scale = self.target_button_width / self.quit_sprite.width
            self.quit_sprite.scale = .12
            self.quit_sprite.left = 22
            self.quit_sprite.center_y = self.button_start_y - 80
            
            print("All images loaded successfully!")
            
        except Exception as e:
            print(f"Error loading images: {e}")
    
    def on_draw(self):
        """Render the screen"""
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        
        # Draw all sprites using arcade.draw_sprite
        if self.domino_sprite:
            arcade.draw_sprite(self.domino_sprite)
        
        if self.play_sprite:
            arcade.draw_sprite(self.play_sprite)
            
        if self.statistics_sprite:
            arcade.draw_sprite(self.statistics_sprite)
            
        if self.settings_sprite:
            arcade.draw_sprite(self.settings_sprite)
            
        if self.quit_sprite:
            arcade.draw_sprite(self.quit_sprite)
    
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks on buttons"""
        # Manual click boundaries based on actual visible button positions
        # Format: (left, right, bottom, top)
        
        # Play button at y=150, left=15, scale=.25
        play_bounds = (15, 115, 135, 165)  # Approximate visible area
        
        # Statistics button at y=110 (150-40), left=24, scale=.2
        stats_bounds = (24, 154, 95, 125)  # Approximate visible area
        
        # Settings button at y=90 (150-60), left=24, scale=.186
        settings_bounds = (24, 139, 75, 105)  # Approximate visible area
        
        # Quit button at y=70 (150-80), left=22, scale=.12
        quit_bounds = (22, 77, 55, 80)  # Approximate visible area
        
        # Check which button was clicked (check from bottom to top)
        if quit_bounds[0] <= x <= quit_bounds[1] and quit_bounds[2] <= y <= quit_bounds[3]:
            print("Quit button clicked - Closing game...")
            arcade.close_window()
        
        elif settings_bounds[0] <= x <= settings_bounds[1] and settings_bounds[2] <= y <= settings_bounds[3]:
            print("Settings button clicked")
            # TODO: Show settings
        
        elif stats_bounds[0] <= x <= stats_bounds[1] and stats_bounds[2] <= y <= stats_bounds[3]:
            print("Statistics button clicked")
            # TODO: Show statistics
        
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