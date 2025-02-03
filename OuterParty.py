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
      - once there are more than n amount of rebel outerParty, random events will happen (low chance of kill outerParty, 
      very low chance of kill proles,  disfunction on ministry's duty, etc)
  """
  def __init__(self,
              model,
              pos,
              loyalty, # the loyalty score defines if rebel or not, the higher the loyalty, the more likely to detect rebel behavoiur
              alive, # is alive
              foodCRate, # the food consumption rate
              foodStock, # current food holding
              senseOfHunger, # the preception of hunger via network effect and the agent's own feeling
              senseOfSafety, # the perception of safegy via network effect
              rebel, # if rebel able to influce other outerParty's loyalty value, have more chance of move randomly
              ministry # the ministry is worked in
              ):
    super().__init__(model)
    pass

  """
    OuterParty can die from 3 ways:
    - bomb attack
    - hunger
    - killed by rebelled proles
    - killed by rebelled outerParty
    - rebelled outerParty killed by Love ministry

    remove from the grid, reduce the number OuterParty in corresponding minitry
  """
  def die(self):
    self.model.grid.remove_agent(self)
    self.model.schedule.remove(self)

  def step(self):
    pass
