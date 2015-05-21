import random
import util
import sfml

from collections import deque
from models.automata import Automata
from models.algae import Algae

class Simulation():
  def __init__(self):
    self.debug = True
    settings = sfml.window.ContextSettings(antialiasing=2)
    self.window = sfml.graphics.RenderWindow(sfml.window.VideoMode(1600, 900), "Automata", sfml.window.Style.DEFAULT, settings)
    self.window.framerate_limit = 120

    self.entities = deque()

    for x in range(1):
      self.spawn("automata")

    for x in range(20):
      self.spawn("algae")

    self.algae_timer = sfml.system.Clock()

    self.font_roboto = sfml.graphics.Font.from_file("resources/Roboto-Light.ttf")
    self.fps_counter = sfml.graphics.Text("0 FPS", self.font_roboto, 24)
    self.fps_counter.color = sfml.graphics.Color(30, 200, 30)
    self.fps_counter.position = (10, 10)

    self.fps_clock = sfml.system.Clock()

  def listen(self):
    for event in self.window.events:
      if type(event) is sfml.window.CloseEvent:
        self.window.close()

      if type(event) is sfml.window.KeyEvent:
        if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.ESCAPE):
          self.window.close()
          
        if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.SPACE):
          pass

        if self.debug and sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.RIGHT):
          for entity in filter(lambda x: x.type is "automata", self.entities):
            entity.shape.rotation += 1

        if self.debug and sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.LEFT):
          for entity in filter(lambda x: x.type is "automata", self.entities):
            entity.shape.rotation -= 1

      if type(event) is sfml.window.MouseButtonEvent:
        if sfml.window.Mouse.is_button_pressed(sfml.window.Mouse.LEFT):
          x, y = event.position
          self.spawn("automata", x=x, y=y)

  def render(self):
    self.window.clear(sfml.graphics.Color(27, 24, 77))

    if self.debug:
      fps = 1000000.0 / self.fps_clock.restart().microseconds
      self.fps_counter.string = "%d FPS" % fps
      self.window.draw(self.fps_counter)

    for item in self.entities:
      self.window.draw(item)

    self.window.display()

  def spawn(self, entity_type, x=None, y=None):
    height, width = self.window.size

    entity_id = util.gen_id()
    pos_x = x or random.randrange(round(height * 0.1), round(height * 0.9))
    pos_y = y or random.randrange(round(width * 0.1), round(width * 0.9))

    if entity_type == "automata":
      entity = Automata(entity_id, pos_x, pos_y, debug=self.debug)
    
    elif entity_type == "algae":
      entity = Algae(entity_id, pos_x, pos_y, debug=self.debug)

    self.entities.append(entity)

  def step(self):
    for entity in self.entities:
      entity.step()

      if entity.objective in ["eat", "eat!", "mate"] and entity.target is None:
        entity.target = util.find_target(entity, self.entities)

    if self.algae_timer.elapsed_time.seconds > 10:
      if random.random() <= 0.5:
        self.algae_timer.restart()
        self.spawn("algae")