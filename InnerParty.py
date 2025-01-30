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
    - They don't really have the Maslow's pyramid need as they symbolizes the party, not real human
  """
  # Here we use class level variable since population belongs to this class
  population = 2

  def __init__(self,
              model,
              pos, # current position
              alive, # is alive
              foodCRate, # food consumption rate
              foodStock, # the current food holding
              ):
    super().__init__(model)
    self.model = model
    self.pos = pos
    self.alive = alive
    self.foodCRate = foodCRate
    self.foodStock = foodStock

  """
    Inner party member can die from two ways:
    - bomb attack
    - hunger

    remove from the grid, reduce the number of InnerParty in All ministries
  """
  def maybe_die(self):
    pass

  """
    Here we use class method, since the function execution is on the InnerParty level
    not for each individual, as long as there is at least 1 inner party survive, the 
    its power still exsits.

    make decision based on request
  """
  @classmethod
  def step(cls, request):
    if cls.population < 1:
      print("*********************************************************")
      print("------------------ BIG BROTHER IS DEAD ------------------")
      print("*********************************************************")
      exit()
    # Based on the request, make the decision
    cls.make_decision(cls, request)
    
  """
    Based on the performance of four ministries, allocating ourterparty and prole resources to
    the four ministries.
  """  
  @classmethod
  def make_decision(cls, metrics):
    pass