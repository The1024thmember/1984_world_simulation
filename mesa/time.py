class RandomActivationByType:
    def __init__(self, model):
        self.model = model
        self._agents = []

    def add(self, agent):
        if agent not in self._agents:
            self._agents.append(agent)

    def remove(self, agent):
        if agent in self._agents:
            self._agents.remove(agent)

    def step(self):
        # This model handles stepping manually; keep for compatibility.
        pass
