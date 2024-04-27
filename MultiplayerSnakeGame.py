from typing import List
from Snake import Snake
from Food import Food


class MultiplayerSnakeGame:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.snakes: List[Snake] = []
        self.foods: List[Food] = []
        self.map = [["" for _ in range(self.width)] for _ in range(self.height)]

    def add_snake(self, snake: Snake):
        self.snakes.append(snake)
        for x, y in snake.body:
            self.map[x][y] = snake.player_id

    def remove_snake(self, player_id: str):
        self.snakes = [snake for snake in self.snakes if snake.player_id != player_id]
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y] == player_id:
                    self.map[x][y] = ""

    def add_food(self, food: Food):
        self.foods.append(food)
        self.map[food.position[0]][food.position[1]] = "food"

    def remove_food(self, position):
        self.foods = [food for food in self.foods if food.position != position]
        self.map[position[0]][position[1]] = ""

    def move_snakes(self):
        for snake in self.snakes:
            snake.move()

    def change_direction(self, player_id, direction):
        for snake in self.snakes:
            if snake.player_id == player_id:
                if (
                    snake.direction == (1, 0)
                    and direction == (-1, 0)
                    or snake.direction == (-1, 0)
                    and direction == (1, 0)
                    or snake.direction == (0, 1)
                    and direction == (0, -1)
                    or snake.direction == (0, -1)
                    and direction == (0, 1)
                ):
                    return
                snake.direction = direction

    def check_collisions(self):
        snake_ids_to_remove = set()
        for snake in self.snakes:
            head = snake.body[0]
            if (
                head[0] < 0
                or head[0] >= self.width
                or head[1] < 0
                or head[1] >= self.height
            ):
                snake_ids_to_remove.add(snake.player_id)
            elif (
                self.map[head[0]][head[1]] != ""
                and self.map[head[0]][head[1]] != "food"
            ):
                print("Collision")
                snake_ids_to_remove.add(snake.player_id)
            elif head in [food.position for food in self.foods]:
                snake.score += 1
                snake.food_eaten += 1
                self.remove_food(head)

        heads = [snake.body[0] for snake in self.snakes]
        for i in range(len(heads)):
            for j in range(i + 1, len(heads)):
                if heads[i] == heads[j]:
                    snake_ids_to_remove.add(self.snakes[i].player_id)
                    snake_ids_to_remove.add(self.snakes[j].player_id)
                    

        for player_id in snake_ids_to_remove:
            self.remove_snake(player_id)
                    

    def update_map(self):
        self.map = [["" for _ in range(self.width)] for _ in range(self.height)]
        for snake in self.snakes:
            for x, y in snake.body:
                self.map[x][y] = snake.player_id
        for food in self.foods:
            self.map[food.position[0]][food.position[1]] = "food"


    def spawn_food(self):
        while len(self.foods) < 20:
            new_food = Food()
            new_food.spawn()
            while self.map[new_food.position[0]][new_food.position[1]] != "":
                new_food.spawn()
            self.add_food(new_food)

    def spawn_snake(self, player_id):
        new_snake = Snake(player_id)
        new_snake.spawn()
        self.add_snake(new_snake)

    def update(self):
        self.move_snakes()
        self.check_collisions()
        self.update_map()
        self.spawn_food()
