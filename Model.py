### Mesa version = 3.0.3

import mesa
class BasicModel(mesa.Model):
  """
  BasicModel simulates the society described in 1984.
  External environment: at war, there will be random bomb attack on random location with random impact from time to time,
  the agent will be killed the agent is placed in the bomb's impact area.

  Internal environment: there are three types of agents, InnerParty, OuterParty, and Proles
  They will be initialized based on certain percentage, and initialized at random location.
  """
  def __init__(
      self,
  ):
    super().__init__()
    pass

  def step(self):
    pass
