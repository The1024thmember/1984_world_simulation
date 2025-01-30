class TruthMinistry():
  """
  Labour: 
    - Inner party: decision making on allocating resources of OuterParty and Proles
    - Outer party: ensure Outerparty and Proles' loyalty score are not dropping

  Function: 
    - Gather the loyalty score for Proles and Outerparty
    - Gather the number of rebelled agents
    - Increase the loyalty score on each step with a small value
    - Cut off the network spread for hunger and safety concerns

  Metricks:
    - The number of agents transformed to be rebel
    - The delta of metricks from last step to current step
  """
  def __init__(self,
               outerParties, # a list of outer party that work for peace ministry
               nInnerParty, # number of inner party
              ):
    self.outerParties = outerParties
    self.nInnerParty = nInnerParty
    pass

  def increaseLoyaltyScore(self):
    """
      Increase loyalty score for every agent by n
    """
    pass

  def cutOffNegativeImpact(self):
    """
      Events like hunger and bomb attack can spread and decrease the loyalty number
      for neighbour agent, reduce the impact of such event on neighbouring agent
    """
    pass

  def getMetricks(self):
    pass


  
  def allocateNewResources(self, resources):
    """
      Allocate new resources for this ministry
    """
    pass