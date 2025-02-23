import random
from Common import CauseOfDeath, Classes


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
    self.numberOfTransformedRebelledAgents = 0
    self.proleLoyaltyScoreIncrease = 10
    self.outerPartiesLoyaltyScoreIncrease = 10

  def increaseLoyaltyScore(self, agents):
    """
      Increase loyalty score for every agent
    """
    for agent in agents:
      if not agent.rebel:
        if isinstance(agent, Classes.OuterParty):
          agent.loyalty += random.uniform(self.outerPartiesLoyaltyScoreIncrease*0.5, self.outerPartiesLoyaltyScoreIncrease)
        elif isinstance(agent, Classes.Proles):
          agent.loyalty += random.uniform(self.proleLoyaltyScoreIncrease*0.8, self.proleLoyaltyScoreIncrease)

  def interfereNegativeImpact(self, cause):
    """
      Events like hunger and bomb attack can spread and decrease the loyalty number
      for neighbour agent, reduce the impact of such event on neighbouring agent
    """
    if cause == CauseOfDeath.Hunger:
      return random.uniform(0.5, 1.0)
    elif cause == CauseOfDeath.BombAttack:
      return random.uniform(0.3, 0.8) 


  def getMetricks(self, agents):
    """
      Collect the number of agents transformed in to rebelled agents
      Calculate the delta
    """
    currentRebelled = 0
    for agent in agents:
      if not agent.rebel and agent.loyalty < 50:
          currentRebelled += 1
    delta = currentRebelled - self.numberOfTransformedRebelledAgents
    self.numberOfTransformedRebelledAgents = currentRebelled # record the current rebelled agents
    return delta, self.numberOfTransformedRebelledAgents 
  
  def allocateNewResources(self, resources):
    """
      Allocate new resources for this ministry
    """
    self.outerParties = resources[Classes.OuterParty]