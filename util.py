import random
from string import ascii_letters, digits

def gen_id(length=10):
  chars = ascii_letters + digits
  return "".join([random.choice(chars) for x in range(length)])

def find_target(searcher, entities):
  def distance(a, b):
    n = a - b
    c = n[0]**2 + n[1]**2

    return c

  origin = searcher.shape.position

  if searcher.objective is "eat" or searcher.objective is "eat!":
    algae = filter(lambda x: x.type is "algae", entities)
    candidates = sorted(algae, key=lambda x: distance(origin, x.shape.position))
    
    return candidates[0] if candidates else None

  if searcher.objective is "mate":
    mates = filter(lambda x: x.objective is "mate" and x.shape.position is not origin, entities)
    candidates = sorted(mates, key=lambda x: distance(origin, x.shape.position))

    return candidates[0] if candidates else None