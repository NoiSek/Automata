import sfml

class Algae(sfml.graphics.Drawable):
  def __init__(self, entity_id, x, y, global_vars={}):
    sfml.graphics.Drawable.__init__(self)

    self.type = "algae"
    self.spawning = True
    self.global_vars = global_vars
    self.shape = sfml.graphics.CircleShape(3.0, 6)
    self.shape.position = (x, y)
    self.shape.fill_color = sfml.graphics.Color(170, 220, 170, 100)
    self.shape.outline_color = sfml.graphics.Color(170, 220, 170)
    self.shape.outline_thickness = 1
    self.shape.origin = (1.5, 1.5)
    self.shape.ratio = (0, 0)

    self.id = entity_id
    self.x = x
    self.y = y

    self.age = 0
    self.objective = "idle"

    self.age_ticker = sfml.system.Clock()
    self.spawn_ticker = sfml.system.Clock()

    self.events = []

    if self.global_vars.get("debug"):
      self.font_roboto = sfml.graphics.Font.from_file("resources/Roboto-Light.ttf")
      self.debug_text = sfml.graphics.Text(self.debug_data(), self.font_roboto, 12)
      self.debug_text.color = sfml.graphics.Color(30, 200, 30)
      self.debug_text.position = (self.x + 15, self.y - 15)

  def debug_data(self):
    if not self.global_vars.get("debug"):
      return False

    return "Age: {age}".format(age=self.age)

  def draw(self, target, states):
    target.draw(self.shape, states)

    if self.global_vars.get("debug"):
      self.debug_text.string = self.debug_data()
      target.draw(self.debug_text, states)

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

    emit = self.events

    del self.events
    self.events = []
    
    return emit 