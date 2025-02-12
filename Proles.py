

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
    self.alpha = 1 # Controls how sharply loyalty impacts spread probability

  def calculateLoyalty(self):
     pass
  
  def rebelSpread(self):
    """
     Spread rebel by lowering neighbour's loyalty score
     Little chance the rebelled prole will be caught by Love ministry
     The higher the neighbour's loyalty score, the lower chance they get affected
    """
    neighbors = self.get_neighbors()
    
    # apply love ministry's monitoring
    if random.random() < self.model.loveMinistry.monitor(Classes.Prole):
       self.model.loveMinistry.rebelQueue.append(self)

    for neighbor in neighbors:
      if not neighbor.is_rebel and isinstance(neighbor, Classes.Proles):
        # Compute spread probability (non-linear)
        loyalty_factor = (100 - neighbor.loyalty)/100  # Lower loyalty = Higher chance
        # apply love ministry's rebel supression randomly
        suppression = self.model.loveMinistry.interfereRebellion(Classes.Prole) if random.randint(0,10) > 5 else 1
        spread_probability = (1 - math.exp(-self.alpha * loyalty_factor)) * suppression        
        if random.random() < spread_probability:
          # dreacse loyalty score
          neighbor.loyalty -= 10

  """
    Proles can die from five ways:
    - bomb attack
    - hunger
    - killed by rebelled proles
    - killed by rebelled outerParty
    - rebelled prole killed by Love ministry    
    
    remove from the grid, reduce the number Proles in corresponding ministry
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

