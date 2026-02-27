class MultiGrid:
    def __init__(self, width, height, torus=False):
        self.width = width
        self.height = height
        self.torus = torus
        self._cells = {}

    def _normalize_pos(self, pos):
        x, y = pos
        if self.torus:
            return (x % self.width, y % self.height)
        return (x, y)

    def place_agent(self, agent, pos):
        pos = self._normalize_pos(pos)
        agent.pos = pos
        self._cells.setdefault(pos, []).append(agent)

    def remove_agent(self, agent):
        pos = agent.pos
        if pos is None:
            return
        agents = self._cells.get(pos, [])
        if agent in agents:
            agents.remove(agent)
            if not agents:
                self._cells.pop(pos, None)
        agent.pos = None

    def move_agent(self, agent, pos):
        self.remove_agent(agent)
        self.place_agent(agent, pos)

    def get_cell_list_contents(self, pos):
        pos = self._normalize_pos(pos)
        return list(self._cells.get(pos, []))

    def get_neighbors(self, pos, radius=1, include_center=False):
        pos = self._normalize_pos(pos)
        x0, y0 = pos
        neighbors = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0 and not include_center:
                    continue
                nx = x0 + dx
                ny = y0 + dy
                if self.torus:
                    nx %= self.width
                    ny %= self.height
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.extend(self.get_cell_list_contents((nx, ny)))
        return neighbors
