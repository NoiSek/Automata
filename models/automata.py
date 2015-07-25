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
    #self.shape.fill_color = sfml.graphics.Color(255, 255, 255, 150)
    self.shape.fill_color = sfml.graphics.Color(200, 200, 200)
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

    self.debug_text = sfml.graphics.Text(self.debug_data(), self.global_vars['font'], 12)
    self.debug_text.color = sfml.graphics.Color(30, 200, 30)
    self.debug_text.position = (self.x + 25, self.y - 75)

    self.debug_target = sfml.graphics.VertexArray(sfml.graphics.PrimitiveType.LINES_STRIP, 2)
    self.debug_target[0].position = self.shape.position
    self.debug_target[1].position = self.aim

    self.debug_direction = sfml.graphics.VertexArray(sfml.graphics.PrimitiveType.LINES_STRIP, 2)
    self.debug_direction[0].position = self.shape.position
    self.debug_direction[1].position = self.shape.position

  def calculate_position(self):
    if self.rotational_velocity is not 0:
      self.shape.rotate(self.rotational_velocity)

    if self.directional_velocity is not 0:
      x, y = self.shape.position
      x_velocity = self.directional_velocity * math.sin(math.radians(self.shape.rotation))
      y_velocity = self.directional_velocity* math.cos(math.radians(self.shape.rotation))

      self.set_position(x + x_velocity, y + -y_velocity)

  def choose_action(self):
    if self.target:
      degrees = self.get_angle_to_target()
      base_speed = self.speed

      if self.objective is "eat!":
        self.base_speed *= 1.5

      if abs(self.rotational_velocity) < 0.35 * base_speed:
        if degrees < 0:
          self.rotational_velocity -= 0.001

        elif degrees > 0:
          self.rotational_velocity += 0.001

      if self.directional_velocity < 0.45 * base_speed:
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
          if self.target.type is "algae":
            self.eat()

        elif self.objective is "mate":
          if self.target.type is not "algae":
            self.mate()

    if self.objective is "idle":
      pass

  def choose_objective(self):
    if self.hunger_ticker.elapsed_time.seconds > 1:
      self.hunger_ticker.restart()
      self.health -= 0.05

    if 7 < self.health:
      if self.age >= 5 and self.mating_ticker.elapsed_time.seconds > 20:
        self.objective = "mate"
      else:
        self.objective = "idle"
        self.target = None

    if 3 < self.health <= 7:
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

  def debug_data(self):
    if not self.global_vars.get("debug"):
      return False

    if self.target:
      target = "{x}, {y}, {angle}".format(
        x=round(self.target.shape.position.x), 
        y=round(self.target.shape.position.y),
        angle=round(self.get_angle_to_target())
      )

    return "Age: {age}\nHunger: {health}\nObjective: {objective}\nTarget: {target}\nRotation: {rotation}\nVelocity: d{d_velocity} r{r_velocity}".format(
        age=round(self.age, 2),
        health=round(self.health, 2),
        objective=self.objective,
        target=target if self.target else "None",
        rotation=round(self.shape.rotation),
        d_velocity=round(self.directional_velocity, 3),
        r_velocity=round(self.rotational_velocity, 3)
      )

  def decay_velocity(self):
    # Decay directional velocity
    if self.directional_velocity > 0:
      if self.directional_velocity - 0.0007 >= 0:
        self.directional_velocity -= 0.0007

      else:
        self.directional_velocity -= 0.0001

    # Decay rotational velocity
    if abs(self.rotational_velocity) > 0:
      if self.rotational_velocity > 0:
        self.rotational_velocity -= 0.0008

      if self.rotational_velocity < 0:
        self.rotational_velocity += 0.0008

  def draw(self, target, states):
    target.draw(self.shape, states)

    if self.global_vars.get("debug"):
      self.debug_text.string = self.debug_data()
      target.draw(self.debug_text, states)

      self.debug_direction[1].position = self.aim
      target.draw(self.debug_direction, states)

      if self.target:
        if round(self.get_angle_to_target()) is 0:
          self.debug_target[0].color = sfml.graphics.Color(150, 255, 150)
          self.debug_target[1].color = sfml.graphics.Color(150, 255, 150)
        else:
          self.debug_target[0].color = sfml.graphics.Color(255, 255, 255)
          self.debug_target[1].color = sfml.graphics.Color(255, 255, 255)

        self.debug_target[1].position = self.target.shape.position
        target.draw(self.debug_target, states)

  def eat(self):
    self.health += 1.6
    self.events.append({
      "type": "eat",
      "subject": self.id, 
      "target": self.target.id
    })

    #del self.target
    self.target = None

  def get_angle_to_target(self, convert=True):
    if not self.target:
      return False

    a = reticle = self.aim
    b = origin = self.shape.position
    c = target = self.target.shape.position

    ab = b - a
    bc = c - b

    dot_product = sum(ab * bc)
    len_ab = math.sqrt(sum(ab * ab))
    len_bc = math.sqrt(sum(bc * bc))
    
    try:
      degrees = math.degrees(math.acos(dot_product / (len_ab * len_bc))) - 180
      self.last_degrees = degrees
    except ZeroDivisionError:
      print("ZeroDivisionError")
      degrees = math.degrees(math.acos(0)) - 180
    except ValueError:
      print("ValueError")
      print(self.last_degrees)
      return self.last_degrees

    determinant = (ab.x * bc.y) - (ab.y * bc.x)

    if determinant < 0:
      return -degrees

    else:
      return degrees

    # This does not work beyond 325 degrees.
    #v1 = math.atan2((reticle.y - origin.y), reticle.x - origin.x)
    #v2 = math.atan2((target.y - origin.y), target.x - origin.x)

    #degrees = abs(math.degrees(v1 - v2))

    # Convert to +- 1-180
    #if degrees > 180 and False:
    #  return degrees - 360

    #else:
    #  return degrees

  def mate(self):
    self.health -= 1.5
    self.mating_ticker.restart()
    
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

  def set_color(self):
    if self.objective is "mate":
      self.shape.fill_color = sfml.graphics.Color(235, 56, 169, 150)
      self.shape.outline_color = sfml.graphics.Color(235, 56, 169)

    elif self.objective in ["eat", "eat!", "idle"]:
      hue, saturation, lightness = 0, 1, 0.65 
      scale = lambda x: ((x / 10) * 115) / 360

      if self.health > 10:
        hue = 115 / 360

      else:
        hue = scale(self.health)

      r, g, b = util.hsl_to_rgb(hue, saturation, lightness)
      self.shape.fill_color = sfml.graphics.Color(r, g, b, 150)
      #self.shape.fill_color = sfml.graphics.Color(max(0, r - 30), max(0, g - 30), max(0, b - 30))
      self.shape.outline_color = sfml.graphics.Color(r, g, b)

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
    self.set_color()

    emit = self.events

    #del self.events
    self.events = []

    return emit

  def update_aim(self):
    direction_x = (75 * math.sin(math.radians(self.shape.rotation))) + self.shape.position.x
    direction_y = -(75 * math.cos(math.radians(self.shape.rotation))) + self.shape.position.y
    self.aim = (direction_x, direction_y)