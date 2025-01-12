### Mesa version = 3.0.3
import mesa
import warnings

# Suppress all UserWarnings, there are some UserWarning and DeprecationWarning
# which spamming the terminal
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class OuterParty(mesa.Agent):
  """
    OuterParty:
    - Have the duty from the four ministries
    - Takes 13% of population
    - Able to move randomly
    - Have the basic need of Maslow's pyramid, and each individual have slightly different variation on its value
    - Have the potential of rebel based on its loyalty value, 
      rebel rule:
      - able to influence neighbour outerParty's loyalty score (randomly decide to influence or not)
      - if neighbour outerParty have higher loyalty score, on influence will results in caught
      - if neighbour outerParty have lower loyalty score, decrease the neighbour outerParty loyalty score
      - the more neighbour is rebel, the more effective in decreasing low loyalty score neighbour outerParty's loyalty score
      rebel action:
      - once there are more than n amount of rebel outerParty, random events will happen (low chance of kill outerParty, very low chance of kill proles,  disfunction on ministry's duty, etc)

  """
  def __init__(self,
              model,
              pos,
              loyalty, # the loyalty score defines if rebel or not, the higher the loyalty, the sharp in response with rebel behavoiur
              alive, # is alive
              foodCRate, # the food consumption rate
              rebel, # if rebel able to influce other outerParty's loyalty value, have more chance of move randomly
              ministry # the ministry is worked in
              ):
    super().__init__(model)
    pass


  def step(self):
    pass
