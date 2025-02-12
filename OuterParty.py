### Mesa version = 3.0.3
import math
import random
import mesa
import warnings

from Common import CauseOfDeath, Classes
from Model import calculateDistance

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
    self.pos = pos
    self.loyalty = loyalty
    self.alive = alive
    self.foodCRate = foodCRate
    self.foodStock = foodStock
    self.senseOfHunger = senseOfHunger
    self.senseOfSafety = senseOfSafety
    self.rebel = rebel
    self.ministry = ministry
    self.alpha = 5 # Controls how sharply loyalty impacts spread probability

  def calculateLoyalty(self):
     pass

  def rebelSpread(self):
    """
     Spread rebel by lowering neighbour's loyalty score
      - able to influence neighbour outerParty's loyalty score (randomly decide to influence or not)
      - if neighbour outerParty have higher loyalty score, on influence will results in caught
      - if neighbour outerParty have lower loyalty score, decrease the neighbour outerParty loyalty score
      - the more neighbour is rebel, the more effective in decreasing low loyalty score neighbour outerParty's loyalty score
    """
    # apply love ministry's monitoring
    if random.random() < self.model.loveMinistry.monitor(Classes.OuterParty):
       self.model.loveMinistry.rebelQueue.append(self)

    # move around
    new_x, new_y = self.model.findSpot()
    self.model.releaseSpot(self.pos)
    self.pos = (new_x, new_y)

    # get the neighbour in the new location
    neighbors = self.get_neighbors()

    # spread rebel only when there is lower loyalty outerParty as neighbour
    for neighbor in neighbors:
      if not neighbor.is_rebel and isinstance(neighbor, Classes.OuterParty):
        loyalty_factor = (100 - neighbor.loyalty)/100 
        if loyalty_factor > 0.4:
          suppression = self.model.loveMinistry.interfereRebellion(Classes.OuterParty) if random.randint(0,10) > 5 else 1
          spread_probability = (1 - math.exp(-self.alpha * loyalty_factor)) * suppression        
          if random.random() < spread_probability:
            # decrease loyalty score
            neighbor.loyalty -= 20           
            
  """
    OuterParty can die from 3 ways:
    - bomb attack
    - hunger
    - killed by rebelled proles
    - killed by rebelled outerParty
    - rebelled outerParty killed by Love ministry

    remove from the grid, reduce the number OuterParty in corresponding minitry
  """
  def die(self, cause):
    self.alive = False
    self.model.grid.remove_agent(self)
    self.model.schedule.remove(self)    
    # Based on the died cause, trigger the following effect
    if cause == CauseOfDeath.Hunger:
      self.spreadSenseOfHunger()
      self.model.plentyMinistry.numberOfDiedAgents[1]+=1
    elif cause == CauseOfDeath.BombAttack:
      self.spreadSenseOfSatefy()
      self.model.numberOfDiedAgents.numberOfDiedAgents[1]+=1

  def consumeFood(self):
    """
    # Food consumption
    # 1. Consume food
    # 2. Calculate Casualty
    # 3. Spread of sense of hunger via network effect
    """
    if self.foodStock < self.foodCRate:
        # step 2,3 : calculate casualty &  Spread of sense of hunger via network effect
        self.die(CauseOfDeath.Hunger)
    else:
        # step 1: Consume food
        self.foodStock -= self.foodCRate
        # When food stock is lower than certain ratio, the sense of hunger will kick in
        foodRatio = self.foodStock / max(1, self.foodCRate) 
        hungerImpact = max(0, 1 - (foodRatio / 3))*10
        self.senseOfHunger += hungerImpact


  def getNeighbors(self, rangeLimit):
      """
      Get all neighboring agents within a given range.
      Assumes there is a function `getAllAgents()` that returns all agents in the grid.
      """
      neighbors = []
      for other in self.getAllAgents():
          if other != self:
              distance = calculateDistance(self, other)
              if distance <= rangeLimit:
                  neighbors.append(other)
      return neighbors
  
  def spreadSenseOfHunger(self):
    """
      Spread the sense of hunger via network effect
      Take account of truthMinistry to interfere with the spreading
    """
    # Get neighbors within the spreading range
    neighbors = self.getNeighbors(self, self.spreadRange)

    for neighbor in neighbors:
        if not neighbor.rebel: # there is no point of updating rebeled agent
          # Hunger impact increases if food stock is low
          foodRatio = neighbor.foodStock / max(1, neighbor.foodCRate) 
          hungerImpact = max(0, 1 - (foodRatio / 5))

          # Distance decay effect
          distance = self.calculateDistance(self, neighbor)
          impact = max(0, hungerImpact * (1 - (distance / self.spreadRange)))

          # TruthMinistry interference
          interference = self.model.truthMinistry.interfereNegativeImpact(CauseOfDeath.Hunger)

          # Apply the spread effect
          effectiveImpact = max(0, min(1, impact * interference))*10

          # Update neighbor’s sense of hunger if above threshold
          if effectiveImpact > 2:
            neighbor.senseOfHunger = min(100, max(1, neighbor.senseOfHunger + effectiveImpact))

  def spreadSenseOfSatefy(self):
    """
      Spread the sense of safety via network effect
      Take account of truthMinistry to interfere with the spreading
    """
    # Get neighbors within the spreading range
    neighbors = self.getNeighbors(self.spreadRange)

    for neighbor in neighbors:
        if not neighbor.rebel: # there is no point of updating rebeled agent
          # Calculate distance decay effect (weaker impact as distance increases)
          distance = self.calculateDistance(self, neighbor)
          impact = max(0, 1 - (distance / self.spreadRange))  # Normalized impact

          # TruthMinistry interference (random fluctuation)
          interference = self.model.truthMinistry.interfereNegativeImpact(CauseOfDeath.BombAttack)

          # Apply the spread effect
          effectiveImpact = max(0, min(1, impact * interference))* 10  

          # Update neighbor’s sense of safety only if the threshold is met
          if effectiveImpact > 2:  # Ensures a meaningful spread
            neighbor.senseOfSafety = min(100, max(1, neighbor.senseOfSafety + effectiveImpact))
  
  
  def step(self):
    pass


