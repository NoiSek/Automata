import sfml

class Automata(sfml.graphics.Drawable):
  def __init__(self, entity_id, x, y, debug=False):
    sfml.graphics.Drawable.__init__(self)

    self.debug = debug
    self.shape = sfml.graphics.CircleShape(15.0, 100)
    self.shape.position = (x, y)
    self.shape.fill_color = sfml.graphics.Color(220, 220, 220)

    self.id = entity_id
    self.x = x
    self.y = y

    self.age = 0
    self.health = 7
    
    self.hunger = sfml.system.Clock()
    self.ticker = sfml.system.Clock()

    self.objective = "idle"
    self.target = None

    if debug:
      self.font_roboto = sfml.graphics.Font.from_file("resources/Roboto-Light.ttf")
      self.debug_text = sfml.graphics.Text(self.debug_data(), self.font_roboto, 12)
      self.debug_text.color = sfml.graphics.Color(30, 200, 30)
      self.debug_text.position = (self.x + 50, self.y - 50)

      self.debug_direction = sfml.graphics.Text("^", self.font_roboto, 24)
      self.debug_direction.color = sfml.graphics.Color(30, 200, 30)
      self.debug_direction.position = (self.x + 10, self.y - 25)

  def debug_data(self):
    if self.debug is False:
      return False

    return "Age: {age}\nHunger: {health}\nObjective: {objective}\nTarget: {target}".format(
        age=self.age,
        health=self.health,
        objective=self.objective,
        target=str(self.target)
      )

  def draw(self, target, states):
    target.draw(self.shape, states)

    if self.debug:
      self.debug_text.string = self.debug_data()
      target.draw(self.debug_text, states)
      target.draw(self.debug_direction, states)

  def check_hunger(self):
    if self.hunger.elapsed_time.seconds > 2:
      self.hunger.restart()
      self.health -= 0.25

    if 6 < self.health:
      if self.age > 5:
        self.objective = "mate"
      else:
        self.objective = "idle"

    if 3 < self.health <= 6:
      self.objective = "eat"

    if 0 < self.health <= 3:
      self.objective = "eat!"

    if self.health < 0:
      self.objective = "die"

  def step(self):
    if self.ticker.elapsed_time.seconds > 5:
      self.ticker.restart()
      self.age += 1

    self.check_hunger()

    return self.objective