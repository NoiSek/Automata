import main

if __name__ == "__main__":
  simulation = main.Simulation()
  
  while simulation.window.is_open:
    simulation.listen()
    simulation.step()
    simulation.render()