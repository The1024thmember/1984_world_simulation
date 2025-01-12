### Mesa version = 3.0.3
import mesa
import warnings

# Suppress all UserWarnings, there are some UserWarning and DeprecationWarning
# which spamming the terminal
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class Proles(mesa.Agent):
  """
    Proles:
    - Do basic production labour work
    - Have the potential of rebel
    - Takes 85% of population
  """
  def __init__(self, model,):
    super().__init__(model)
    pass


  def step(self):
    pass
