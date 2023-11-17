class Agent:
    def __init__(self, params):
        self.params = params

    def step(self, screenshots, mode = 'recording'):
        # Implement the logic for the agent's step here
        return ((512, 512), "left", "")