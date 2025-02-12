import random
from Common import Classes, RebelProleActions


class PeaceMinistry():
  """
  Labour: 
    - Inner party: decision making on allocating resources of OuterParty and Proles
    - Outer party: ensure efficiency on defending bomb attack
    - Proles: produce weapons needed for defending bomb attack

  Function: 
    - Defending bomb attack

  Metricks:
    - The number of agents killed in current step
    - The delta of metricks from last step to current step
  """
  def __init__(self,
               proles, # a list of prole that work for peace that work for peace ministry
               outerParties, # a list of outer party that work for peace ministry
               nInnerParty, # number of inner party
               ):
    self.proles = proles
    self.outerParties = outerParties
    self.nInnerParty = nInnerParty
    self.weapons = 0 # number of weapon built
    self.numberOfDiedAgents = [0,0] # indicate the [previous step number of agent died, the current step number of agent died]
    pass

  def collectWeapons(self):
    """
      Collect weapons built by proles
    """
    # generate weapon
    for each in self.proles:
      if each.rebel == RebelProleActions.Misfunction:
        # produce much less weapon than normal
        self.weapons=each.weaponPRate * 0.1
      else:
        self.weapons=each.foodPRate

  def defendBombAttack(self, bomb):
    """
      Defend bomb attack based on the number of Weapons and the number of OuterParty
    """
    # Bomb attack, shuffle to ensure when apply weapon to defend, ensure randomness
    affectedArea = bomb.attack()
    random.shuffle(affectedArea) 
    # Defending the bomb attack
    # 1. The more outerparty there are, the more precision it is in predicting the center location and radius for bomb attack
    # 2. The more weapon there are the higher probablity that the defend on each grid location will work

    center_x, center_y, radius, intensity = bomb.historicalAttacks[-1]
    # Step 1: Calculate precision based on outer party members
    precision = 0
    for each in self.outerParties:
      if each.rebel != RebelProleActions.Misfunction:
        precision += 0.14 # this is due to there can be 6 outerparty on peace ministry, if all of them are work their best, should be 85% of precision

    # Step 2: Predict the attack center and radius using precision
    predicted_center_x = center_x + random.randint(-int((1 - precision) * radius), int((1 - precision) * radius))
    predicted_center_y = center_y + random.randint(-int((1 - precision) * radius), int((1 - precision) * radius))
    predicted_radius = max(1, int(radius * precision))  # Higher precision reduces radius error

    # Step 3: Identify the predicted area
    predicted_area = []
    for dx in range(-predicted_radius, predicted_radius + 1):
        for dy in range(-predicted_radius, predicted_radius + 1):
            if dx**2 + dy**2 <= predicted_radius**2:
                predicted_x = predicted_center_x + dx
                predicted_y = predicted_center_y + dy
                if (predicted_x, predicted_y) in affectedArea:
                    predicted_area.append((predicted_x, predicted_y))
 
    # Step 4: Apply defense using weapons
    defended_area = []
    for (x, y) in predicted_area:
        if self.weapons >= intensity:
            # Each intensity weapons give a 60% chance to defend a location
            if random.random() < 0.6:  # 60% success probability
                defended_area.append((x, y))
                affectedArea.remove((x, y))  # Successfully defended

            # Weapons are consumed
            self.weapons -= intensity

    # Remaining affected area after defense
    attackedLocation = affectedArea
    return attackedLocation
 
  def getMetricks(self):
    """
      Collect the number of agents died because of bomb attack
      Calculate the delta
    """
    pass

  def allocateNewResources(self, resources):
    """
      Allocate new resources for this ministry
    """
    self.proles=resources[Classes.Proles]
    self.outerParties=resources[Classes.OuterParty]