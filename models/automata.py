import sfml
import math
import random

class Automata(sfml.graphics.Drawable):
  def __init__(self, entity_id, x, y, debug=False):
    sfml.graphics.Drawable.__init__(self)

    self.type = "automata"
    self.spawning = True
    self.debug = debug
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
    
    self.hunger_ticker = sfml.system.Clock()
    self.age_ticker = sfml.system.Clock()
    self.spawn_ticker = sfml.system.Clock()

    self.objective = "spawn"
    self.target = None
    self.aim = self.shape.position

    if debug:
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
    if self.debug is False:
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

    if self.debug:
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
    self.shape.rotate(self.rotational_velocity * self.speed)

    if self.directional_velocity is not 0:
      x, y = self.shape.position
      x_velocity = self.directional_velocity * math.cos(self.shape.rotation)
      y_velocity = self.directional_velocity * math.sin(self.shape.rotation)

      self.set_position(x + x_velocity, y + y_velocity)

  def choose_action(self):
    if self.objective is "eat" or self.objective is "eat!":
      if self.target:
        degrees = self.get_angle_to_target()

        if degrees < 0:
          self.rotational_velocity += 0.001

        elif degrees > 0:
          self.rotational_velocity -= 0.001

        if round(degrees) is 0:
          self.rotational_velocity = 0
          self.directional_velocity += 0.001

  def choose_objective(self):
    if self.hunger_ticker.elapsed_time.seconds > 2:
      self.hunger_ticker.restart()
      self.health -= 0.25

    if 6 < self.health:
      if self.age > 5:
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

  def get_angle_to_target(self):
    if not self.target:
      return False
        
    origin = self.shape.position
    reticle = self.debug_direction[1].position
    target = self.target.shape.position

    angle1 = math.atan2(reticle.y - origin.y, reticle.x - origin.x)
    angle2 = math.atan2(target.y - origin.y, target.x - origin.x)

    degrees = math.degrees(angle1 - angle2)

    # Convert to +- 1-180
    if degrees > 180:
      return -(180 + (180 - degrees))

    else:
      return degrees

  def set_position(self, x, y):
    if self.debug:
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

    return self.objective

  def update_aim(self):
    direction_x = (75 * math.sin(math.radians(self.shape.rotation))) + self.shape.position.x
    direction_y = -(75 * math.cos(math.radians(self.shape.rotation))) + self.shape.position.y
    self.aim = (direction_x, direction_y)