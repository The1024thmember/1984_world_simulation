class DataCollector:
    def __init__(self, model_reporters=None, agent_reporters=None):
        self.model_reporters = model_reporters or {}
        self.agent_reporters = agent_reporters or {}

    def collect(self, model):
        pass
