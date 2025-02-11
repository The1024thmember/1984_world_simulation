import math
import random
from Common import CauseOfDeath, Classes


class LoveMinistry():
  """
  Labour: 
    - Inner party: decision making on allocating resources of OuterParty and Proles
    - Outer party: 
      - ensure proper monitoring on Outerparty and Proles via anti-network rebel spreading
      - transformation or killing of rebelled OuterParty
      - kill rebelled Proles

  Function: 
    - Keep track on rebelled agents in a queue
    - Execute anti-rebel functionality 
    - Execute agent transformation or killing

  Metricks:
    - The number of rebelled agents in the queue
    - The delta of metricks from last step to current step
  """
  def __init__(self,
               outerParties, # a list of outer party that work for peace ministry
               nInnerParty, # number of inner party
               ):
    self.outerParties = outerParties
    self.nInnerParty = nInnerParty
    self.rebelQueue = []
    self.numberOfQueuedRebelledAgents = 0
    pass

  def interfereRebellion(self, agentType):
    if agentType == Classes.OuterParty:
      return 0.9 # almost no suppression on rebel spreading
    elif agentType == Classes.Proles:
      return 0.3 # quite high suppression on rebel spreading

  def monitor(self, agentType):
    if agentType == Classes.OuterParty:
      return 0.7 # sharp monitoring
    elif agentType == Classes.Proles:
      return 0.2 # loose monitoring

  def transformAgent(self, agent):
    """
     Transform agent to have very high loylaty score
    """
    agent.loyalty = 100
    agent.rebel = False

  def executeAgent(self, agent):
    """
     Execute the agent
    """
    agent.die(CauseOfDeath.Execution)

  def processRebelCase(self):
    """
      FIFO get n agent from rebel queue, n depends on the number of outerParty in LoveMinistry
      Decide to transform outerParty agent or execute outerParty agent
      Execute proles
    """
    numberOfCase = math.ceil(len(self.outerParties)//2)
    while numberOfCase > 0:
      rebelledAgent = self.rebelQueue.pop(0)
      if isinstance(rebelledAgent, Classes.Proles):
        self.executeAgent(rebelledAgent)
      if isinstance(rebelledAgent, Classes.OuterParty):
        executeOuterParty = random.choice([True,False])
        if executeOuterParty:
          self.executeAgent(rebelledAgent)
        else:
          self.transformAgent(rebelledAgent)



  def getMetricks(self):
    """
      Collect the number of rebelled agents in the queue
      Calculate the delta
    """
    pass

  
  def allocateNewResources(self, resources):
    """
      Allocate new resources for this ministry
    """
    self.outerParties = resources[Classes.OuterParty]