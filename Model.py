### Mesa version = 3.0.3
import mesa
import random


class BasicModel(mesa.Model):
  """
  BasicModel simulates the society described in 1984.
  External environment: at war, there will be random bomb attack on random location with random impact from time to time,
  the agent will be killed the agent is placed in the bomb's impact area.

  Internal environment: there are three types of agents, InnerParty, OuterParty, and Proles
  They will be initialized based on certain percentage, and initialized at random location.


  In this model, the population will be a dynamic value, since there are few ways that agent can die from this model,
  (check for maybe_die() function in each agent model for detail) and the goal is to see how long the society will last.
  """
  def __init__(
      self,
      width=50,
      height=50, 
      initial_population = 200,
  ):
    super().__init__()

    # Initiate width and height og the sugar space
    self.width = width
    self.height = height
    # Initiate mesa grid class
    self.grid = mesa.space.MultiGrid(
        width = self.width, 
        height = self.height, 
        torus = True
      )

    # initiate data collector
    self.datacollector = mesa.DataCollector(
      model_reporters = {},
      agent_reporters = {}
    )

    # Scheduler
    self.schedule = mesa.time.RandomActivationByType(self)

    # Initialize a random number generator
    self.random = random.Random()
    self.initial_population = initial_population

    # Initialize InnerParty

    # Initialize OuterParty

    # Initialize Proles

    # Initialize bomb attack


  """
  Proles should do their production
  OuterParty should fulfill their duty
  InnerParty should fulfill their duty
  Bomb should prepare to attack randomly
  """
  def step(self):
    pass
