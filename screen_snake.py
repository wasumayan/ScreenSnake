import sys
import os
import random
import json
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap, QImage
import glob

# Helper for PyInstaller asset paths
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

SPEED = 100     # Base milliseconds per move
HIGH_SCORE_FILE = 'high_scores.json'
FOOD_IMAGE = 'princeton_logo.png'

DIRECTIONS = {
    Qt.Key_Up: (0, -1),
    Qt.Key_Down: (0, 1),
    Qt.Key_Left: (-1, 0),
    Qt.Key_Right: (1, 0)
}

class ScreenSnake(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.show()
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Simple grid setup
        self.screen_width = self.width()
        self.screen_height = self.height()
        self.cell_size = 25
        self.grid_width = self.screen_width // self.cell_size
        self.grid_height = self.screen_height // self.cell_size
        self.offset_x = (self.screen_width - self.grid_width * self.cell_size) // 2
        self.offset_y = (self.screen_height - self.grid_height * self.cell_size) // 2
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_step)
        
        # Speed management
        self.base_speed = SPEED
        self.current_speed = SPEED
        self.speed_level = 0
        
        # AI difficulty management
        self.ai_reaction_delay = True  # AI has reaction delay initially
        self.ai_difficulty_threshold = 15  # Remove handicap after 15 points
        
        # Load images
        self.food_pixmap = QPixmap(resource_path(FOOD_IMAGE))
        if self.food_pixmap.isNull():
            print(f"Warning: Could not load food image: {FOOD_IMAGE}")
        else:
            print(f"Successfully loaded food image: {FOOD_IMAGE}")
            self.food_pixmap_scaled = self.food_pixmap.scaled(self.cell_size, self.cell_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Find rival logos (use os.listdir for PyInstaller compatibility)
        logo_dir = resource_path('.')
        self.rival_logo_files = [os.path.join(logo_dir, f) for f in os.listdir(logo_dir) if f.endswith('_logo.png') and 'princeton' not in f]
        self.rival_logos = {}
        self.rival_colors = {}
        self._load_rival_logos()
        
        self.spawned_rival_logos = set()
        self.elapsed_time = 0
        self.spawn_interval = 60  # seconds
        self.spawn_timer = QTimer(self)
        self.spawn_timer.timeout.connect(self.check_spawn_new_rival)
        self.spawn_timer.start(1000)  # check every second
        
        self.reset_game()
        self.load_high_scores()

    def _load_rival_logos(self):
        """Load rival logo images"""
        for logo_file in self.rival_logo_files:
            pixmap = QPixmap(logo_file)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.cell_size, self.cell_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.rival_logos[logo_file] = scaled_pixmap
                self.rival_colors[logo_file] = self._extract_dominant_color(logo_file)
            else:
                print(f"Warning: Could not load rival logo: {logo_file}")

    def _extract_dominant_color(self, filename):
        """Extract dominant color from logo"""
        image = QImage(filename)
        color_count = {}
        for x in range(0, image.width(), 4):  # Sample every 4th pixel for speed
            for y in range(0, image.height(), 4):
                color = image.pixelColor(x, y)
                if color.alpha() > 200:  # Only non-transparent pixels
                    rgb = (color.red(), color.green(), color.blue())
                    color_count[rgb] = color_count.get(rgb, 0) + 1
        if color_count:
            dominant = max(color_count, key=color_count.get)
            return QColor(*dominant, 220)
        return QColor(128, 128, 128, 220)

    def _calculate_speed(self, score):
        """Calculate speed based on score - faster every 5 points"""
        speed_level = score // 5
        speed_increase = speed_level * 10  # 10ms faster per level
        new_speed = max(30, self.base_speed - speed_increase)  # Minimum 30ms
        return new_speed, speed_level

    def _update_speed(self):
        """Update game speed based on current score"""
        new_speed, new_level = self._calculate_speed(self.score)
        if new_speed != self.current_speed:
            self.current_speed = new_speed
            self.speed_level = new_level
            self.timer.setInterval(self.current_speed)
            print(f"Speed increased! Level {self.speed_level}, Speed: {self.current_speed}ms")
        
        # Check if AI should become smarter
        if self.ai_reaction_delay and self.score >= self.ai_difficulty_threshold:
            self.ai_reaction_delay = False
            print("AI snakes are now at full intelligence!")

    def reset_game(self):
        """Reset the game state"""
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.ai_snakes = []
        self.spawned_rival_logos = set()
        self.elapsed_time = 0
        self.score = 0
        self.paused = False
        self.game_over = False
        self.extra_food = set()
        
        # Reset speed
        self.current_speed = self.base_speed
        self.speed_level = 0
        
        # Reset AI difficulty
        self.ai_reaction_delay = True
        
        # Spawn initial AI snake
        if self.rival_logo_files:
            logo_file = random.choice(self.rival_logo_files)
            self.spawned_rival_logos.add(logo_file)
            start_pos = self._find_safe_spawn_position()
            ai_snake = {
                'body': [start_pos],
                'logo_file': logo_file,
                'logo_pixmap': self.rival_logos[logo_file],
                'color': self.rival_colors[logo_file],
            }
            self.ai_snakes.append(ai_snake)
            print(f"Spawned AI snake with logo: {logo_file}")
        
        self.spawn_food()
        self.timer.start(self.current_speed)
        self.update()

    def _find_safe_spawn_position(self):
        """Find a safe position to spawn AI snake"""
        for attempt in range(50):
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)
            if (pos not in self.snake and 
                (not hasattr(self, 'food') or pos != self.food) and
                all(pos not in ai['body'] for ai in self.ai_snakes)):
                return pos
        return (0, 0)  # Fallback

    def spawn_food(self):
        """Spawn food at random position"""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            food = (x, y)
            if (food not in self.snake and 
                all(food not in ai['body'] for ai in self.ai_snakes) and 
                food not in self.extra_food):
                self.food = food
                break

    def game_step(self):
        """Main game loop step"""
        if self.paused or self.game_over:
            return
        
        # Move player snake
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % self.grid_width, (head_y + dy) % self.grid_height)
        
        # Check collision
        if (new_head in self.snake or 
            any(new_head in ai['body'] for ai in self.ai_snakes)):
            self.game_over = True
            self.save_high_score()
            self.timer.stop()
            self.update()
            return
        
        self.snake = [new_head] + self.snake
        
        # Check food eating
        ate_food = False
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
            ate_food = True
            # Check if speed should increase
            self._update_speed()
        elif new_head in self.extra_food:
            self.score += 1
            self.extra_food.remove(new_head)
            ate_food = True
            # Check if speed should increase
            self._update_speed()
        
        if not ate_food:
            self.snake.pop()
        
        # Move AI snakes (simplified)
        dead_ai_indices = []
        for idx, ai in enumerate(self.ai_snakes):
            if not ai['body']:
                continue
            self._move_ai_snake(ai)
            
            # Check AI collision
            ai_head = ai['body'][0]
            if ai_head in self.snake or ai_head in ai['body'][1:]:
                self.extra_food.update(ai['body'][1:])
                dead_ai_indices.append(idx)
            elif ai_head == self.food:
                # AI snake eats food - let it grow
                self.spawn_food()
            else:
                # AI snake didn't eat food, remove tail
                ai['body'].pop()
        
        # Remove dead AI snakes
        for idx in sorted(dead_ai_indices, reverse=True):
            print(f"AI snake {idx} died")
            del self.ai_snakes[idx]
        
        # Debug: print AI snake count
        if len(self.ai_snakes) == 0:
            print(f"No AI snakes remaining. Elapsed time: {self.elapsed_time}")
        
        self.update()

    def _move_ai_snake(self, ai):
        """Simple AI movement with reaction delay"""
        if not ai['body']:
            return
        
        head_x, head_y = ai['body'][0]
        fx, fy = self.food
        
        # Check if player is very close (for reaction delay)
        player_head = self.snake[0]
        distance_to_player = abs(head_x - player_head[0]) + abs(head_y - player_head[1])
        player_is_close = distance_to_player <= 2  # Within 2 grid spaces
        
        # Simple movement toward food
        possible_moves = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx = (head_x + dx) % self.grid_width
            ny = (head_y + dy) % self.grid_height
            new_pos = (nx, ny)
            
            if (new_pos not in ai['body'] and 
                new_pos not in self.snake and
                all(new_pos not in other['body'] for other in self.ai_snakes)):
                dist = abs(nx - fx) + abs(ny - fy)
                possible_moves.append(((dx, dy), dist))
        
        if possible_moves:
            # Choose move closest to food
            possible_moves.sort(key=lambda x: x[1])
            dx, dy = possible_moves[0][0]
            
            # Apply reaction delay if enabled and player is close
            if self.ai_reaction_delay and player_is_close:
                # 50% chance to not move when player is close (reaction delay)
                if random.random() < 0.5:
                    dx, dy = 0, 0
        else:
            # No safe move, don't move
            dx, dy = 0, 0
        
        new_head = ((head_x + dx) % self.grid_width, (head_y + dy) % self.grid_height)
        ai['body'] = [new_head] + ai['body']

    def check_spawn_new_rival(self):
        """Spawn new rival snake every 60 seconds"""
        if self.game_over or self.paused:
            return
        
        self.elapsed_time += 1
        if self.elapsed_time % self.spawn_interval == 0:
            available_logos = [f for f in self.rival_logo_files if f not in self.spawned_rival_logos]
            if available_logos:
                logo_file = random.choice(available_logos)
                self.spawned_rival_logos.add(logo_file)
                start_pos = self._find_safe_spawn_position()
                ai_snake = {
                    'body': [start_pos],
                    'logo_file': logo_file,
                    'logo_pixmap': self.rival_logos[logo_file],
                    'color': self.rival_colors[logo_file],
                }
                self.ai_snakes.append(ai_snake)
                print(f"Spawned new rival snake with logo: {logo_file}")
            else:
                print(f"No more logos available to spawn. All spawned: {self.spawned_rival_logos}")
        
        # Debug: print current AI snake count every 10 seconds
        if self.elapsed_time % 10 == 0:
            print(f"Time: {self.elapsed_time}s, AI snakes: {len(self.ai_snakes)}")

    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() in DIRECTIONS:
            new_dir = DIRECTIONS[event.key()]
            if (new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]) or len(self.snake) == 1:
                self.next_direction = new_dir
        elif event.key() == Qt.Key_P:
            self.paused = not self.paused
            self.update()
        elif event.key() == Qt.Key_Space:
            if self.game_over:
                self.reset_game()
        elif event.key() == Qt.Key_Escape:
            QApplication.quit()

    def mousePressEvent(self, event):
        """Exit on mouse click"""
        QApplication.quit()

    def focusOutEvent(self, event):
        """Pause when window loses focus"""
        self.paused = True
        self.update()

    def focusInEvent(self, event):
        """Resume when window gains focus"""
        self.update()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.fillRect(self.rect(), Qt.transparent)
            
            # Draw score
            painter.setPen(QColor(255, 255, 255, 240))
            painter.setFont(QFont('Arial', 28, QFont.Bold))
            painter.drawText(30, 80, f'Score: {self.score}')
            
            # Draw AI snakes
            for ai in self.ai_snakes:
                for i, (x, y) in enumerate(ai['body']):
                    px = self.offset_x + x * self.cell_size
                    py = self.offset_y + y * self.cell_size
                    if i == 0:  # Head
                        logo_pixmap = ai.get('logo_pixmap')
                        if logo_pixmap and not logo_pixmap.isNull():
                            painter.drawPixmap(px, py, logo_pixmap)
                        else:
                            painter.setBrush(ai.get('color', QColor(128, 128, 128, 220)))
                            painter.setPen(Qt.NoPen)
                            painter.drawEllipse(px, py, self.cell_size, self.cell_size)
                    else:  # Body
                        painter.setBrush(ai.get('color', QColor(128, 128, 128, 220)))
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(px, py, self.cell_size, self.cell_size)
            
            # Draw extra food
            painter.setBrush(QColor(255, 0, 0, 200))
            painter.setPen(Qt.NoPen)
            for pos in self.extra_food:
                if pos is not None:
                    x, y = pos
                    painter.drawEllipse(self.offset_x + x * self.cell_size, self.offset_y + y * self.cell_size, self.cell_size, self.cell_size)
            
            # Draw player snake
            for i, (x, y) in enumerate(self.snake):
                px = self.offset_x + x * self.cell_size
                py = self.offset_y + y * self.cell_size
                if i == 0:  # Head with eyes
                    painter.setBrush(QColor(255, 140, 0, 230))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(px, py, self.cell_size, self.cell_size)
                    
                    # Draw eyes
                    eye_radius = self.cell_size // 6
                    eye_offset_x = self.cell_size // 4
                    eye_offset_y = self.cell_size // 3
                    dx, dy = self.direction
                    
                    if dx == 1:  # Right
                        ex1 = px + self.cell_size - eye_offset_x*2
                        ex2 = px + self.cell_size - eye_offset_x*2
                        ey1 = py + eye_offset_y
                        ey2 = py + self.cell_size - eye_offset_y - eye_radius
                    elif dx == -1:  # Left
                        ex1 = px + eye_offset_x
                        ex2 = px + eye_offset_x
                        ey1 = py + eye_offset_y
                        ey2 = py + self.cell_size - eye_offset_y - eye_radius
                    elif dy == 1:  # Down
                        ex1 = px + eye_offset_x
                        ex2 = px + self.cell_size - eye_offset_x - eye_radius
                        ey1 = py + self.cell_size - eye_offset_y*2
                        ey2 = py + self.cell_size - eye_offset_y*2
                    else:  # Up
                        ex1 = px + eye_offset_x
                        ex2 = px + self.cell_size - eye_offset_x - eye_radius
                        ey1 = py + eye_offset_y
                        ey2 = py + eye_offset_y
                    
                    painter.setBrush(QColor(255, 255, 255, 240))
                    painter.drawEllipse(ex1, ey1, eye_radius, eye_radius)
                    painter.drawEllipse(ex2, ey2, eye_radius, eye_radius)
                    painter.setBrush(QColor(0, 0, 0, 240))
                    painter.drawEllipse(ex1 + eye_radius//2, ey1 + eye_radius//2, eye_radius//2, eye_radius//2)
                    painter.drawEllipse(ex2 + eye_radius//2, ey2 + eye_radius//2, eye_radius//2, eye_radius//2)
                else:  # Body with stripes
                    painter.setBrush(QColor(255, 140, 0, 200))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(px, py, self.cell_size, self.cell_size)
                    if i % 2 == 0:
                        painter.setBrush(QColor(0, 0, 0, 180))
                        stripe_width = self.cell_size // 4
                        painter.drawRect(px + self.cell_size//2 - stripe_width//2, py, stripe_width, self.cell_size)
            
            # Draw food
            if hasattr(self, 'food') and self.food is not None:
                fx, fy = self.food
                if hasattr(self, 'food_pixmap_scaled') and self.food_pixmap_scaled and not self.food_pixmap_scaled.isNull():
                    painter.drawPixmap(self.offset_x + fx * self.cell_size, self.offset_y + fy * self.cell_size, self.food_pixmap_scaled)
                else:
                    painter.setBrush(QColor(255, 0, 0, 200))
                    painter.drawEllipse(self.offset_x + fx * self.cell_size, self.offset_y + fy * self.cell_size, self.cell_size, self.cell_size)
            
            # Draw high scores
            painter.setFont(QFont('Arial', 16))
            for i, hs in enumerate(getattr(self, 'high_scores', [])[:5]):
                painter.drawText(self.offset_x + self.grid_width * self.cell_size + 20, self.offset_y + 30 + i * 25, f'#{i+1}: {hs}')
            
            # Draw pause/game over
            if getattr(self, 'paused', False):
                painter.setPen(QColor(255, 255, 255, 200))
                painter.setFont(QFont('Arial', 48, QFont.Bold))
                painter.drawText(self.rect(), Qt.AlignCenter, 'PAUSED')
            if getattr(self, 'game_over', False):
                painter.setPen(QColor(255, 0, 0, 220))
                painter.setFont(QFont('Arial', 48, QFont.Bold))
                top_score = max(getattr(self, 'high_scores', [self.score])) if getattr(self, 'high_scores', None) else self.score
                painter.drawText(self.rect(), Qt.AlignCenter, f'GAME OVER\nScore: {self.score}\nTop Score: {top_score}\nPress SPACE to restart')
        except Exception as e:
            import traceback
            print("Exception in paintEvent:", e)
            traceback.print_exc()

    def save_high_score(self):
        """Save high score"""
        self.high_scores.append(self.score)
        self.high_scores = sorted(self.high_scores, reverse=True)[:5]
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(self.high_scores, f)
        except Exception:
            pass

    def load_high_scores(self):
        """Load high scores"""
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                self.high_scores = json.load(f)
        except Exception:
            self.high_scores = []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreenSnake()
    window.show()
    sys.exit(app.exec_()) 