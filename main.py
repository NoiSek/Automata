import random
import sfml

from collections import deque
from models.automata import Automata
from models.algae import Algae
from string import ascii_letters, digits

class Simulation():
  def __init__(self):
    self.debug = True
    settings = sfml.window.ContextSettings(antialiasing=2)
    self.window = sfml.graphics.RenderWindow(sfml.window.VideoMode(1600, 900), "Automata", sfml.window.Style.DEFAULT, settings)
    self.window.framerate_limit = 60

    self.entities = deque()

    for x in range(2):
      self.spawn("automata")

    for x in range(10):
      self.spawn("algae")

    self.algae_timer = sfml.system.Clock()

  def gen_id(self, length=10):
    chars = ascii_letters + digits
    return "".join([random.choice(chars) for x in range(length)])

  def listen(self):
    for event in self.window.events:
      if type(event) is sfml.window.CloseEvent:
        self.window.close()

      if type(event) is sfml.window.KeyEvent:
        if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.ESCAPE):
          self.window.close()
          
        if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.SPACE):
          pass

  def render(self):
    self.window.clear(sfml.graphics.Color(27, 24, 77))

    for item in self.entities:
      self.window.draw(item)

    self.window.display()

  def spawn(self, entity_type):
    height, width = self.window.size

    entity_id = self.gen_id()
    pos_x = random.randrange(round(height * 0.1), round(height * 0.9))
    pos_y = random.randrange(round(width * 0.1), round(width * 0.9))

    if entity_type == "automata":
      entity = Automata(entity_id, pos_x, pos_y, debug=self.debug)
    
    elif entity_type == "algae":
      entity = Algae(entity_id, pos_x, pos_y, debug=self.debug)

    self.entities.append(entity)

  def step(self):
    for entity in self.entities:
      entity.step()

    if self.algae_timer.elapsed_time.seconds > 10:
      if random.random() <= 0.5:
        self.algae_timer.restart()
        self.spawn("algae")