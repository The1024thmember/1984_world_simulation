
from Common import Classes, RebelProleActions, RebelOuterPartyActions


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
               diffusionRate = 0.25, # Percentage of food to distribute to neighbors
               varianceThreshold = 0.5, # Variance threshold to determine convergence
              ):
    self.proles = proles
    self.outerParties = outerParties
    self.nInnerParty = nInnerParty
    self.numberOfDiedAgents = [0,0] # indicate the [previous step number of agent died, the current step number of agent died]
    self.diffusionRate = diffusionRate
    self.varianceThreshold = varianceThreshold
    pass

  # TODO - need to fix the agentSpot variable, maybe we don't need to record the (x,y) at all
  def generateAndDistributeFood(self, agentsSpot, gridSize):
    """
      Locate the proles location, generate food on this location
      Use network diffusion, distribute food to every agent based on their location
      Agents then put the newly distruibuted food into their stock for consumption

      Keep in mind that this function should take the number of OuterParty and rebel 
      and etc as input, as it impacts the food generation and distruibution process
    """
    agents = [agent for agent in agentsSpot if getattr(agent, "pos", None) is not None and agent.alive]
    if not agents:
      return

    # food generation
    total_food = 0
    for each in self.proles:
      if not each.alive:
        continue
      amount = each.foodPRate
      if each.rebel_action == RebelProleActions.Misfunction:
        amount = each.foodPRate * 0.1
      total_food += amount

    # distribution efficiency depends on outer party performance
    misfunction = sum(1 for each in self.outerParties if each.rebel_action == RebelOuterPartyActions.Misfunction)
    efficiency = max(0.2, 1.0 - (0.05 * misfunction))
    total_food *= efficiency

    per_agent = total_food / len(agents)
    for agent in agents:
      agent.foodStock += per_agent


  def getMetricks(self):
    """
      Collect the number of agents died because of bomb attack
      Calculate the delta
    """
    delta = self.numberOfDiedAgents[1] - self.numberOfDiedAgents[0]
    self.numberOfDiedAgents[0] = self.numberOfDiedAgents[1] # record the current step of number of died agents
    return delta, self.numberOfDiedAgents[0] 

  
  def allocateNewResources(self, resources):
    """
      Allocate new resources for this ministry
    """
    self.proles = resources[Classes.Proles]
    self.outerParties = resources[Classes.OuterParty]

    
