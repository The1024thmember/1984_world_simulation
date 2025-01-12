### Mesa version = 3.0.3
import mesa
import warnings

# Suppress all UserWarnings, there are some UserWarning and DeprecationWarning
# which spamming the terminal
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class InnerParty(mesa.Agent):
  """
    InnerParty:
    - Make decisions requested from the 4 ministries
    - Takes 2% of population
  """
  def __init__(self, model,):
    super().__init__(model)
    pass


  def step(self):
    pass
