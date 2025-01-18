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
               nOuterParty,
               nInnerParty):
    pass