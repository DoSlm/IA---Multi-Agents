
from turtle import width


class Agent:
    width
    grid = []
    other_agents = []
    current_state = 0
    terminal_state = 0

    def __init__(_width, _current_state, _terminal_state):
        pass

    def run(self):
        while(self.current_state != self.terminal_state):
            self.observe()
            self.search()
            self.apply()

    def observe(self):
        pass

    def search(self):
        pass

    def apply(self):
        pass

