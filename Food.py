import random


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self):
        self.position = (random.randint(0, 19), random.randint(0, 19))
