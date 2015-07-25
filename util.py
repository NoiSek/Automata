import random
import colorsys

from collections import deque
from string import ascii_letters, digits

def gen_id(length=10):
  chars = ascii_letters + digits
  return "".join([random.choice(chars) for x in range(length)])

def delete(target, entities):
  entities = filter(lambda x: x.id is target, entities)
  return deque(entities)

def distance(a, b):
  n = a - b
  c = n[0]**2 + n[1]**2

  return c

def find_target(searcher, entities):
  origin = searcher.shape.position

  if searcher.objective in ["eat", "eat!"]:
    algae = filter(lambda x: x.type is "algae", entities)
    candidates = sorted(algae, key=lambda x: distance(origin, x.shape.position))
    
    return candidates[0] if candidates else None

  if searcher.objective is "mate":
    mates = filter(lambda x: x.objective is "mate" and x.type is searcher.type and x.id is not searcher.id, entities)
    candidates = sorted(mates, key=lambda x: distance(origin, x.shape.position))

    return candidates[0] if candidates else None

def hsl_to_rgb(h, s, l):
  values = colorsys.hls_to_rgb(h, l, s)
  values = [round(x * 255) for x in values]
  return values