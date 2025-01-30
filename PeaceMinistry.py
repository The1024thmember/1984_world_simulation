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
    self.agentsDiedOfBomb = 0
    pass

  def collectWeapons(self):
    """
      Collect weapons built by proles
    """
    for each in self.proles:
      self.weapons += each.weaponPRate

  def defendBombAttack(self):
    """
      Defend bomb attack based on the number of Weapons and the number of OuterParty
    """
    pass

  def getMetricks(self, diedAgents):
    """
      Return the number of agents died because of bomb attack
      As well as the current resources allocated to this ministry
    """
    pass

  def allocateNewResources(self, resources):
    """
      Allocate new resources for this ministry
    """
    pass