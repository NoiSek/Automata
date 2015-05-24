import sfml
import math
import util
import random

class Automata(sfml.graphics.Drawable):
  def __init__(self, entity_id, x, y, global_vars={}):
    sfml.graphics.Drawable.__init__(self)

    self.type = "automata"
    self.spawning = True
    self.global_vars = global_vars
    self.shape = sfml.graphics.CircleShape(15.0, 3)
    self.shape.position = (x, y)
    self.shape.fill_color = sfml.graphics.Color(255, 255, 255, 150)
    self.shape.outline_color = sfml.graphics.Color(255, 255, 255)
    self.shape.outline_thickness = 2
    self.shape.origin = (15, 15)
    self.shape.ratio = (0, 0)
    self.shape.rotation = random.randrange(0, 359)

    self.rotational_velocity = 0
    self.directional_velocity = 0

    self.id = entity_id
    self.x = x
    self.y = y

    self.age = 0
    self.health = 7
    self.speed = 1
    
    self.age_ticker = sfml.system.Clock()
    self.hunger_ticker = sfml.system.Clock()
    self.spawn_ticker = sfml.system.Clock()
    self.mating_ticker = sfml.system.Clock()
    self.movement_ticker = sfml.system.Clock()

    self.objective = "spawn"
    self.target = None
    self.aim = self.shape.position

    # For emitting state changes. algae eaten, mating, etc.
    self.events = []

    if self.global_vars.get("debug"):
      self.font_roboto = sfml.graphics.Font.from_file("resources/Roboto-Light.ttf")
      self.debug_text = sfml.graphics.Text(self.debug_data(), self.font_roboto, 12)
      self.debug_text.color = sfml.graphics.Color(30, 200, 30)
      self.debug_text.position = (self.x + 25, self.y - 75)

      self.debug_target = sfml.graphics.VertexArray(sfml.graphics.PrimitiveType.LINES_STRIP, 2)
      self.debug_target[0].position = self.shape.position
      self.debug_target[1].position = self.aim

      self.debug_direction = sfml.graphics.VertexArray(sfml.graphics.PrimitiveType.LINES_STRIP, 2)
      self.debug_direction[0].position = self.shape.position
      self.debug_direction[1].position = self.shape.position

  def debug_data(self):
    if not self.global_vars.get("debug"):
      return False

    if self.target:
      target = "{id} - {x}, {y}, {angle}".format(
        id=self.target.id, 
        x=self.target.shape.position.x, 
        y=self.target.shape.position.y,
        angle=self.get_angle_to_target()
      )

    return "Age: {age}\nHunger: {health}\nObjective: {objective}\nTarget: {target}\nRotation: {rotation}\nVelocity: d{d_velocity} r{r_velocity}".format(
        age=self.age,
        health=self.health,
        objective=self.objective,
        target=target if self.target else "None",
        rotation=self.shape.rotation,
        d_velocity=self.directional_velocity,
        r_velocity=self.rotational_velocity
      )

  def draw(self, target, states):
    target.draw(self.shape, states)

    if self.global_vars.get("debug"):
      self.debug_text.string = self.debug_data()
      target.draw(self.debug_text, states)

      self.debug_direction[1].position = self.aim
      target.draw(self.debug_direction)

      if self.target:
        if round(self.get_angle_to_target()) is 0:
          self.debug_target[0].color = sfml.graphics.Color(150, 255, 150)
          self.debug_target[1].color = sfml.graphics.Color(150, 255, 150)
        else:
          self.debug_target[0].color = sfml.graphics.Color(255, 255, 255)
          self.debug_target[1].color = sfml.graphics.Color(255, 255, 255)

        self.debug_target[1].position = self.target.shape.position
        target.draw(self.debug_target, states)

  def calculate_position(self):
    base_speed = self.speed

    if self.objective is "eat!":
      self.base_speed *= 1.5

    if self.rotational_velocity is not 0:
      self.shape.rotate(self.rotational_velocity * base_speed)

    if self.directional_velocity is not 0:
      x, y = self.shape.position
      x_velocity = (self.directional_velocity * base_speed) * math.sin(math.radians(self.shape.rotation))
      y_velocity = (self.directional_velocity * base_speed) * math.cos(math.radians(self.shape.rotation))
      #x_velocity = self.directional_velocity * math.cos(math.radians(self.shape.rotation))
      #y_velocity = self.directional_velocity * math.sin(math.radians(self.shape.rotation))

      self.set_position(x + x_velocity, y + -y_velocity)

  def choose_action(self):
    if self.target:
      degrees = self.get_angle_to_target()

      if degrees < 0:
        self.rotational_velocity += 0.001

      elif degrees > 0:
        self.rotational_velocity -= 0.001

      if 5 < abs(round(degrees)) <= 10:
        #if self.movement_ticker.elapsed_time.milliseconds > 500:
        #  self.directional_velocity += 0.0025
        
        self.directional_velocity += 0.001

      elif abs(round(degrees)) <= 5:
        #if self.movement_ticker.elapsed_time.milliseconds > 500:
        #  self.directional_velocity += 0.005
        
        self.directional_velocity += 0.003

      elif round(degrees) is 0:
        #if self.movement_ticker.elapsed_time.milliseconds > 500:
        #  self.directional_velocity += 0.01

        self.directional_velocity += 0.005

      distance_to_target = util.distance(self.shape.position, self.target.shape.position)
      
      if distance_to_target < 50:
        if self.objective in ["eat", "eat!"]:
          self.eat()

        if self.objective is "mate":
          self.mate()
          self.mating_ticker.restart()

    if self.objective is "idle":
      pass

  def choose_objective(self):
    if self.hunger_ticker.elapsed_time.seconds > 2:
      self.hunger_ticker.restart()
      self.health -= 0.25

    if 6 < self.health:
      if self.age >= 5 and self.mating_ticker.elapsed_time.seconds > 10:
        self.objective = "mate"
      else:
        self.objective = "idle"
        self.target = None

    if 3 < self.health <= 6:
      self.objective = "eat"

    if 0 < self.health <= 3:
      self.objective = "eat!"

    if self.health < 0:
      self.objective = "die"
      
      self.directional_velocity = 0
      self.rotational_velocity = 0

      self.events.append({
        "type": "die",
        "subject": self.id, 
        "target": self.id
      })

  def decay_velocity(self):
    # Decay directional velocity
    if self.directional_velocity > 0:
      self.directional_velocity -= 0.0005

    # Decay rotational velocity
    if abs(self.rotational_velocity) > 0:
      if self.rotational_velocity > 0:
        self.rotational_velocity -= 0.0008

      if self.rotational_velocity < 0:
        self.rotational_velocity += 0.0008

  def eat(self):
    self.health += 3
    self.events.append({
      "type": "eat",
      "subject": self.id, 
      "target": self.target.id
    })

    del self.target
    self.target = None

  def get_angle_to_target(self, convert=True):
    if not self.target:
      return False
        
    origin = self.shape.position
    reticle = self.debug_direction[1].position
    target = self.target.shape.position

    angle1 = math.atan2(reticle.y - origin.y, reticle.x - origin.x)
    angle2 = math.atan2(target.y - origin.y, target.x - origin.x)

    degrees = math.degrees(angle1 - angle2)

    # Convert to +- 1-180
    if degrees > 180 and convert:
      return degrees - 360

    else:
      return degrees

  def mate(self):
    self.events.append({
      "type": "mate",
      "subject": self.id, 
      "target": self.target.id
    })

  def set_position(self, x, y):
    if self.global_vars.get("debug"):
      self.debug_text.position = (x + 25, y - 75)
      self.debug_target[0].position = (x, y)
      self.debug_direction[0].position = (x, y)

    self.shape.position = (x, y)

  def step(self):
    if self.spawning:
      if self.spawn_ticker.elapsed_time.milliseconds > 25:
        self.shape.ratio += 0.05
        self.spawn_ticker.restart()

      if round(self.shape.ratio.x, 1) == 1:
        self.spawning = False
        del self.spawn_ticker
    
    if self.age_ticker.elapsed_time.seconds > 5:
      self.age_ticker.restart()
      self.age += 1

    if self.age < 80:
      self.speed = 1 - (self.age / 100)

    else:
      self.speed = 0.2

    self.calculate_position()
    self.update_aim()
    self.choose_objective()
    self.choose_action()
    self.decay_velocity()

    emit = self.events

    del self.events
    self.events = []

    return emit

  def update_aim(self):
    direction_x = (75 * math.sin(math.radians(self.shape.rotation))) + self.shape.position.x
    direction_y = -(75 * math.cos(math.radians(self.shape.rotation))) + self.shape.position.y
    self.aim = (direction_x, direction_y)