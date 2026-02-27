class Agent:
    def __init__(self, model):
        self.model = model
        self.pos = None

    def get_neighbors(self, radius=1, include_center=False):
        if self.model is None or self.model.grid is None:
            return []
        return self.model.grid.get_neighbors(self.pos, radius=radius, include_center=include_center)
