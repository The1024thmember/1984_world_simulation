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
              pos,
              alive,
              foodCRate,
              ):
    super().__init__(model)
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
    Based on request from four ministries, allocating ourterparty and prole resources to
    the four ministries.
  """  
  @classmethod
  def make_decision(cls, request):
    pass