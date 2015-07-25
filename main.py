import random
import util
import sfml

from collections import deque
from models.automata import Automata
from models.algae import Algae

class Simulation():
  def __init__(self):
    self.global_vars = { "debug": True }
    self.fps_enabled = True
    settings = sfml.window.ContextSettings(antialiasing=2)
    self.window = sfml.graphics.RenderWindow(sfml.window.VideoMode(1600, 900), "Automata", sfml.window.Style.DEFAULT, settings)
    self.window.framerate_limit = 120

    self.entities = deque()
    self.algae_timer = sfml.system.Clock()
    self.font_roboto = sfml.graphics.Font.from_file("resources/Roboto-Light.ttf")
    self.global_vars['font'] = self.font_roboto

    self.fps_counter = sfml.graphics.Text("0 FPS", self.font_roboto, 24)
    self.fps_counter.color = sfml.graphics.Color(30, 200, 30)
    self.fps_counter.position = (10, 10)

    self.fps_clock = sfml.system.Clock()

    for x in range(10):
      self.spawn("automata")

    for x in range(25):
      self.spawn("algae")

  def handle_events(self, local_events):
    # Future animations go here
    for event in local_events:
      if event["type"] is "eat":
        new_entities = filter(lambda x: x.id is not event['target'], self.entities)
        self.entities = deque(new_entities)

      elif event["type"] is "die":
        new_entities = filter(lambda x: x.id is not event['target'], self.entities)
        self.entities = deque(new_entities)

      elif event["type"] is "mate":
        checksum = lambda n: sum([ord(x) for x in n])

        # Mother is whichever has the larger checksum
        if checksum(event['subject']) > checksum(event['target']):
          entity = list(filter(lambda x: x.id is event['subject'], self.entities))[0]
          position = entity.shape.position
          
          position.x += random.randrange(-15, 15)
          position.y += random.randrange(-15, 15)

          self.spawn("automata", x=position.x, y=position.y)

      elif event['type'] is "grow":
        entity = list(filter(lambda x: x.id is event['subject'], self.entities))
        
        if len(entity) > 0:
          entity = entity[0]
        else:
          # The entity has been eaten, most likely.
          return

        position = entity.shape.position

        pos_x = position.x + random.randrange(-25, 25)
        pos_y = position.y + random.randrange(-25, 25)

        self.spawn("algae", x=pos_x, y=pos_y)

  def listen(self):
    for event in self.window.events:
      if type(event) is sfml.window.CloseEvent:
        self.window.close()

      if type(event) is sfml.window.KeyEvent:
        if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.ESCAPE):
          self.window.close()
          
        if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.SPACE):
          for entity in filter(lambda x: x.type is "automata", self.entities):
            entity.directional_velocity += 0.5

        if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.D):
          self.global_vars['debug'] = not self.global_vars['debug']

        if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.F):
          self.fps_enabled = not self.fps_enabled

        if self.global_vars.get("debug") and sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.RIGHT):
          for entity in filter(lambda x: x.type is "automata", self.entities):
            entity.shape.rotation += 1

        if self.global_vars.get("debug") and sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.LEFT):
          for entity in filter(lambda x: x.type is "automata", self.entities):
            entity.shape.rotation -= 1

        if self.global_vars.get("debug") and sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.Q):
          for entity in filter(lambda x: x.type is "automata", self.entities):
            entity.rotational_velocity -= 0.1

        if self.global_vars.get("debug") and sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.E):
          for entity in filter(lambda x: x.type is "automata", self.entities):
            entity.rotational_velocity += 0.1

      if type(event) is sfml.window.MouseButtonEvent:
        x, y = event.position

        if sfml.window.Mouse.is_button_pressed(sfml.window.Mouse.LEFT):
          self.spawn("automata", x=x, y=y)
          print("Spawned Automata at %d, %d" % (x, y))

        if sfml.window.Mouse.is_button_pressed(sfml.window.Mouse.RIGHT):
          self.spawn("algae", x=x, y=y)
          print("Spawned Algae at %d, %d" % (x, y))

  def render(self):
    self.window.clear(sfml.graphics.Color(27, 24, 77))

    if self.fps_enabled:
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
      entity = Automata(entity_id, pos_x, pos_y, global_vars=self.global_vars)
    
    elif entity_type == "algae":
      entity = Algae(entity_id, pos_x, pos_y, global_vars=self.global_vars)

    self.entities.append(entity)

  def step(self):
    local_events = []

    for entity in self.entities:
      response = entity.step()
      local_events.extend(response)

      if entity.objective in ["eat", "eat!", "mate"]:
        entity.target = util.find_target(entity, self.entities)

    self.handle_events(local_events)

    if self.algae_timer.elapsed_time.seconds > 5:
      if random.random() <= 0.5:
        self.algae_timer.restart()
        self.spawn("algae")