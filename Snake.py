import random


class Snake:
    def __init__(self, player_id):
        self.player_id = player_id
        self.body = []
        self.direction = (0, 0)
        self.score = 0
        self.food_eaten = 0

    def spawn(self):
        self.body = [(random.randint(5, 15), random.randint(5, 15))]
        self.direction = (1, 0)
        self.score = 0

    def move(self):

        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        self.body.insert(0, new_head)
        if self.food_eaten > 0:
            self.food_eaten -= 1
        else:
            self.body.pop()
