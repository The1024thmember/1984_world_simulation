

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
      - all forms of production rate dropps dramatically
      - chance of kill proles and very rare chance of kill outerParty
  """
  def __init__(self, 
               model,
               pos,
               loyalty, # the loyalty score defines if rebel or not
               alive, # is alive
               foodCRate, # the food consumption rate
               foodPRate, # the food production rate
               foodStock, # the current food holding
               senseOfHunger, # the preception of hunger via network effect and the agent's own feeling
               senseOfSafety, # the perception of safegy via network effect
               weaponPRate, # the weapon production rate
               rebel, # if rebel descrease neighbour loyalty score
               ministry # the ministry prole is in (Peace or Plenty)
               ):
    super().__init__(model)
    self.model = model
    self.pos = pos
    self.loyalty = loyalty
    self.alive = alive
    self.foodCRate = foodCRate
    self.foodPRate = foodPRate
    self.foodStock = foodStock
    self.senseOfHunger = senseOfHunger
    self.senseOfSafety = senseOfSafety
    self.weaponPRate = weaponPRate
    self.rebel = rebel
    self.ministry = ministry

  """
    Initialize MaslowPyramid
  """
  def initMaslowPyramid(self):
    pass

  def rebelSpread(self):
    """
     Spread rebel by lowering neighbour's loyalty score
    """
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
  def die(self):
    self.model.grid.remove_agent(self)
    self.model.schedule.remove(self)

  def step(self):
    pass
