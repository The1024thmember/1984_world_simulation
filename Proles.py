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
    - Takes 85% of population
    - Have the basic need of Maslow's pyramid, and each individual have slightly different variation on its value
    - Have the potential of rebel based on its loyalty value
    rebel rule:
      - once rebel, spreading towards neighbour prole is for sure
      - all forms of production rate goes to 0
      - chance of kill proles and very rare chance of kill outerParty
  """
  def __init__(self, 
               model,
               pos,
               loyalty, # the loyalty score defines if rebel or not
               alive, # is alive
               foodCRate, # the food consumption rate
               foodPRate, # the food production rate
               weaponPRate, # the weapon production rate
               rebel # if rebel descrease neighbour loyalty score
               ):
    super().__init__(model)
    pass

  """
    Initialize MaslowPyramid
  """
  def initMaslowPyramid(self):
    pass


  """
    Proles can die from five ways:
    - bomb attack
    - hunger
    - killed by rebelled proles
    - killed by rebelled outerParty
    - rebelled prole killed by Love ministry    
    
    remove from the grid, reduce the number Proles in corresponding ministry
  """
  def maybe_die(self):
    pass

  def step(self):
    pass
