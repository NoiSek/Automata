import sfml

class Algae(sfml.graphics.Drawable):
  def __init__(self, entity_id, x, y, debug=False):
    sfml.graphics.Drawable.__init__(self)

    self.debug = debug
    self.shape = sfml.graphics.CircleShape(3.0, 6)
    self.shape.position = (x, y)
    self.shape.fill_color = sfml.graphics.Color(170, 220, 170, 100)
    self.shape.outline_color = sfml.graphics.Color(170, 220, 170)
    self.shape.outline_thickness = 1

    self.id = entity_id
    self.x = x
    self.y = y

    self.age = 0

    self.ticker = sfml.system.Clock()

    if debug:
      self.font_roboto = sfml.graphics.Font.from_file("resources/Roboto-Light.ttf")
      self.debug_text = sfml.graphics.Text(self.debug_data(), self.font_roboto, 12)
      self.debug_text.color = sfml.graphics.Color(30, 200, 30)
      self.debug_text.position = (self.x + 15, self.y - 15)

  def debug_data(self):
    if self.debug is False:
      return False

    return "Age: {age}".format(age=self.age)

  def draw(self, target, states):
    target.draw(self.shape, states)

    if self.debug:
      self.debug_text.string = self.debug_data()
      target.draw(self.debug_text, states)

  def step(self):
    if self.ticker.elapsed_time.seconds > 5:
      self.ticker.restart()
      self.age += 1