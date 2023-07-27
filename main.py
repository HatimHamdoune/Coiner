import pygame
from random import randint


class Sprite:
    WINDOW_SIZE = 1000, 613
    SCOREBOARD_SIZE = 1000, 50
    def __init__(self, filename):
        self._model = pygame.image.load(filename + ".png")
        self._width = self._model.get_width()
        self._height = self._model.get_height()
        self.y_coordinate = 0
        self.x_coordinate = 50
        self.window_width = Sprite.WINDOW_SIZE[0]
        self.window_height = Sprite.WINDOW_SIZE[1]

    @property
    def model(self):
        return self._model
    
    @property
    def coordinates(self):
        return self.x_coordinate, self.y_coordinate
    
    @property
    def hitbox(self):
        return self.x_coordinate, self.x_coordinate + self._width, self.y_coordinate, self.y_coordinate + self._height
    
    def touches_hitbox(self, second_object):
        left_edge_touches = self.hitbox[0] <= second_object.hitbox[1] < self.hitbox[1]
        right_edge_touches = self.hitbox[0] <= second_object.hitbox[0] < self.hitbox[1]
        top_edge_touches = self.hitbox[2] <= second_object.hitbox[3] < self.hitbox[3]
        bottom_edge_touches = self.hitbox[2] <= second_object.hitbox[2] < self.hitbox[3]
        return  (left_edge_touches or right_edge_touches) and (top_edge_touches or bottom_edge_touches)

class Robot(Sprite):
    def __init__(self, filename):
        super().__init__(filename)
        self.y_coordinate = self.window_height - self._height - 50 #50 being the scoreboard height
        self.x_coordinate = self.window_width / 2 - self._width / 2
        self.moving_left = False
        self.moving_right = False

    
    def move(self):
        if self.moving_left and self.x_coordinate > 0:
            self.x_coordinate -= 5
        if self.moving_right and self.x_coordinate < self.window_width - self._width:
            self.x_coordinate += 5

    def respawn(self):
        self.x_coordinate = self.window_width / 2 - self._width / 2
        self.y_coordinate = self.window_height - self._height - 50




class Coin(Sprite):
    def __init__(self, filename):
        super().__init__(filename)
        self.x_coordinate = randint(0, self.window_width - self._width)
        #we respawn the coin off screen, hence the negative value of the y coordinates, i used double the screen height so they don't spawn at the same time
        self.y_coordinate = randint(-2 * self.window_height, -self._height)
        self._move_speed = 1

    def respawn(self):
        self.x_coordinate = randint(0, self.window_width - self._width)
        self.y_coordinate = randint(-2 * self.window_height, -self._height)

    def continue_falling(self):
        self.y_coordinate += self._move_speed

    def change_move_speed(self, movement):
        self._move_speed = movement
    
    




class Ghost(Coin):
    def __init__(self, filename):
        super().__init__(filename)

        




class Coiner:

    def __init__(self) -> None:
        pygame.init()

        self.window_height = 613
        self.window_width = 1000
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Coiner")
        self.clock = pygame.time.Clock()
        
        self.robot = Robot("robot")
        self.ghosts = []
        self.coins = []
        self.score = 0
        self.difficulty = 1

        self.game_still_ongoing = True
        self.you_won = False
        self.you_lost = False
        self.initialize_mobs()
        self.main_loop()


    def initialize_mobs(self):
        for i in range(10):
            self.coins.append((Coin("coin")))
        self.ghosts.append(Ghost("monster"))
        

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.robot.moving_left = True
                if event.key == pygame.K_d:
                    self.robot.moving_right = True
                if event.key == pygame.K_ESCAPE:
                    exit()
                if event.key == pygame.K_F2:
                    self.new_game()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.robot.moving_left = False
                if event.key == pygame.K_d:
                    self.robot.moving_right = False

    def main_loop(self):
        while True:
            self.check_events()
            self.check_game_state()
            self.refresh_window()

    def refresh_window(self):
        self.window.fill((128, 128, 128))
        self.draw_mobs()
        self.draw_scoreboard()
        if self.you_won:
            self.game_won()
        if self.you_lost:
            self.game_lost()
        pygame.display.flip()
        self.clock.tick(60)

    def draw_scoreboard(self):
        scoreboard_size = 50
        pygame.draw.rect(self.window, (0, 0, 0), ((0, self.window_height - scoreboard_size), (self.window_width, scoreboard_size)))
        font = pygame.font.SysFont("Arial", 32)
        scoreboard = font.render(f"Score: {self.score}              Difficulty: {self.difficulty}             F2: New Game", True, (255, 0, 0))
        self.window.blit(scoreboard, (200, self.window_height - scoreboard_size))
    
    def draw_mobs(self):
        for ghost in self.ghosts:
            self.window.blit(ghost.model, (ghost.coordinates))
        for coin in self.coins:
            self.window.blit(coin.model, (coin.coordinates))
        self.window.blit(self.robot.model, self.robot.coordinates)

    def amp_difficulty(self):
        if self.difficulty < 10:
            self.difficulty += 1
            self.coins.pop()
            self.ghosts.append(Ghost("monster"))
            for ghost in self.ghosts:
                ghost.change_move_speed(self.difficulty)
            for coin in self.coins:
                coin.change_move_speed(self.difficulty)
        else:
            self.game_won()

    def check_game_state(self):
        if self.game_still_ongoing:
            self.robot.move()
            if self.score % 10 == 0 and self.score != 0 and self.score >= self.difficulty * 10:
                self.amp_difficulty()
            for coin in self.coins:
                if self.robot.touches_hitbox(coin):
                    self.score += 1
                    coin.respawn()
                if coin.coordinates[1] > self.window_height:
                    coin.respawn()
                else:
                    coin.continue_falling()
            for ghost in self.ghosts:
                if self.robot.touches_hitbox(ghost):
                    self.game_lost()
                if ghost.coordinates[1] > self.window_height:
                    ghost.respawn()
                else:
                    ghost.continue_falling()
        if self.you_won:
            self.game_won()
        if self.you_lost:
            self.game_lost()


    def new_game(self):
        self.ghosts.clear()
        self.coins.clear()
        self.initialize_mobs()
        self.robot.respawn()
        self.score = 0
        self.difficulty = 1
        self.game_still_ongoing = True
        self.you_lost = False
        self.you_won = False
        

    def game_lost(self):
        font = pygame.font.SysFont("Arial", 120)
        text = font.render("You Lost!", True, (255, 0, 0))
        self.window.blit(text, (300, 100))
        self.game_still_ongoing = False
        self.you_lost = True


    def game_won(self):
        font = pygame.font.SysFont("Arial", 80)
        text = font.render("Winner Winner Chicken Dinner!", True, (255, 0, 0))
        self.window.blit(text, (50, 100))
        self.game_still_ongoing = False
        self.you_won = True



if __name__ == "__main__":
    Coiner()




    
        
    
        