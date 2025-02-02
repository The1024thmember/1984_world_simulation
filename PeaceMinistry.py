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
    self.numberOfDiedAgents = 0
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
    # Bomb attack
    bomb.attack()
    


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