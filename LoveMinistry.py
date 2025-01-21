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
    pass

  def antiRebelSpread(self):
    """
     Stop the spread of rebel between proles and between outerparties
    """
    pass

  def transformAgent(self):
    """
     Transform agent to have very high loyaty score
    """
    pass

  def executeAgent(self):
    """
     Execute the agent
    """
    pass

  def processRebelCase(self):
    """
      FIFO get n agent from rebel queue, n depends on the number of outerParty in PeaceMinistry
      Decide to transform outerParty agent or execute outerParty agent
      Execute proles
    """

  def getMetricks(self):
    pass