class PlentyMinistry():
  """
  Labour: 
    - Inner party: decision making on allocating resources of OuterParty and Proles
    - Outer party: ensure food distruibution efficiency via network diffusion
    - Proles: produce food

  Function: 
    - Collecting and distruibute food to every agents

  Metricks:
    - The number of agents died from hunger
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
    self.agentDiedOfHunger = 0
    pass

  def distributeFood(self):
    """
      Use network diffusion, distribute food to every agent
    """
    pass

  def getMetricks(self, diedAgents):
    """
      Return the number of agents died because of hunger
    """
    pass