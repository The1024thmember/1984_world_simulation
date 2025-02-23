### Objectives:
- To observe the evolvement of the society with the define structure similar to the 1984
- To experiment with the hyper parameters and observe their impact on the society's evolvement

### Structure

##### Major concepts:
**Hierarchy classes:**
- Inner party (2%)
- Outer party (13%)
- Proles (85%)

**Government department:**
- Ministry of Plenty
- Ministry of Peace
- Ministry of Love
- Ministry of Truth

**Human needs:** ( based on `Maslow's pyramid`), different class has different requirement and means for satisfaction
- Physiological Needs
- Safety Needs
- Love/Belongingness Needs

**Role in society:**
- Inner party: assign roles for outer party member, decision on 
- Outer party: fulfil their responsibilities
- Prole: produce food, raw material

##### Mapping of Ministries to Basic Needs for Each Class in _1984_

| **Basic Needs**              | **Proles (85%)**                                                       | **Outer Party (13%)**                                             | **Inner Party (2%)**                                                           | **Responsible Ministry**                     |
| ---------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------- |
| **Physiological Needs**      | - **Ministry of Plenty:** Provides food and basic goods                | - **Ministry of Plenty:** Manages resource allocation             | - **Ministry of Plenty:** Ensures access to luxury goods                       | **Ministry of Plenty**                       |
| **Safety Needs**             | - **Ministry of Peace:** Maintains war to ensure order                 | - **Ministry of Love:** Implements surveillance and control       | - **Ministry of Love:** Oversees high-level surveillance and internal security | **Ministry of Peace** & **Ministry of Love** |
| **Love/Belongingness Needs** | - **Ministry of Truth:** Provides entertainment to foster social bonds | - **Ministry of Truth:** Disseminates propaganda to shape beliefs | - **Ministry of Truth:** Controls information to maintain elite cohesion       | **Ministry of Truth**                        |

| **Ministry**           | **Primary Functions**                                                              | **Associated Classes**           |
| ---------------------- | ---------------------------------------------------------------------------------- | -------------------------------- |
| **Ministry of Truth**  | Propaganda dissemination, information control, historical revisionism              | Outer Party, Inner Party         |
| **Ministry of Peace**  | Management of war efforts, military operations                                     | Outer Party, Inner Party         |
| **Ministry of Love**   | Law enforcement, surveillance (Thought Police), punishment, suppression of dissent | Inner Party, Outer Party         |
| **Ministry of Plenty** | Economic production, resource allocation, rationing                                | Proles, Outer Party, Inner Party |

We will simulate the war for random attacks (bomb attacks), the job for ministry of peace will be allocate resources for removing bomb attacks, 

The ministry of peace  consists of outer party, allocate production resources from prole to create weapons.  
- Requests from Inner party - Proles
- Effect on Inner party, outer party and proles, since the bomb attack is location based (survival or not), a failed defend on bomb attack will dramatically increase the safety needs of neighbourhood if ministry of truth does not intervene.

The ministry of plenty overlooks the production for food
- Requests for inner party - Proles
- Effect on inner party, outer party and proles, since all of them consumes food (Physiological Needs), a not hunger group of proles will dramatically increase the physiological needs if ministry of truth does not intervene.

The ministry of Love majorly monitor Outer party, rarely on Proles,
- Requests from inner party - Outer party member
- Effect on outer party (surveillance, punishment) and proles (surveillance, punishment, entertaining?)
	- Needs more interaction, the entertaining for proles based on the book is more self-evolved, the inner party doesn't really interfere, we probably need some general score for proles for deciding if they want to rebel, and how the interaction from outer party to proles encourages rebel.

The ministry of truth generates information
- Requests from inner party - Outer party member
- Effect on proles (safety need), if not function properly, rebel from proles.


##### Interaction between ministries and classes

| **Ministry**           | **Interaction with Proles**                                                              | **Interaction with Outer Party**                                                                                                                                                      | **Interaction with Inner Party**                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Ministry of Love**   | o: kill rebelled proles                                                                  | i: ensure ministry of love's normal function - proper monitoring and transforming<br><br>o: monitoring and transform rebelled outer party either by kill or reshape with high loyalty | i: need decision from inner party on resources allocation                                                         |
| **Ministry of Peace**  | i: uses labor for weapon maunfacturing<br><br>o: ensure prole won't die from bomb attack | i: ensure ministry of peace's normal function - proles labour are effective<br><br>o: ensure outer party won't die from bomb attack                                                   | i: need decision from inner party on resources allocation<br><br>o: ensure inner party won't die from bomb attack |
| **Ministry of Truth**  | o: increases proles loyalty                                                              | i: ensure ministry of truth's normal function <br><br>o: increase outer party's loyalty                                                                                               | i: need decision from inner party on resources allocation                                                         |
| **Ministry of Plenty** | i: uses labour for food production<br><br>o: allocate food to prole                      | i: ensure ministry of plenty's normal function <br><br>o: allocate food to Outer party<br><br>                                                                                        | i: need decision from inner party on resources allocation<br><br>o: allocate food to inner party<br>              |


#### The rebel spreading mechanism:
The equation:
$$ P_{\text{spread}} = 1 - e^{-\alpha (1 - \text{loyalty})} $$

is an **exponential growth function** that determines the probability of rebellion spreading based on **loyalty** and a **scaling factor** `α`.
<img src="https://github.com/user-attachments/assets/51506273-c945-474e-919a-d6cf500884f2" width="500">

#####  What Happens When `α` Increases?

`α` (alpha) is a **scaling factor** that controls how sharply `P_spread` increases as **loyalty decreases**.

1. **Higher `α` Means More Aggressive Spread**
    
    - The probability of spreading rebellion **increases faster** for low-loyalty agents.
    - Even agents with moderate loyalty will have a much higher chance of rebelling.
2. **Loyalty Has Less Buffer**
    
    - With a **low α**, only **very low-loyalty** agents are at risk of rebelling.
    - With a **high α**, even **moderate-loyalty** agents can rebel easily.
	
#####  What does it mean in the model:

1. For prole, a lower alpha value has been used, since prole are less educated and less active in their thought, the rebel can only spread when they are quite unhappy with their environment
2. For Outer party, a higher alpha value has been used due to their work nature, their "double thought" and their experience in how the government works in mind controlling, so they are quite easy to be influenced with new idea
