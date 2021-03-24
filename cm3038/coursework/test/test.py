import cm3038.coursework.waterJugProblem as jug

def state_str():
    world = jug.WaterJugWorld(5, 3)
    start = jug.WaterJugState(world, 0, 0)
    print(start.__str__())

def action():
    world = jug.WaterJugWorld(5, 3)
    start = jug.WaterJugState(world, 0, 0)
    action1 = jug.WaterJugAction(jug.ActionType.FILL, jug.Jug.A)
    state1 = start.apply_action(action1)
    print(action1)
    print(state1)
    action2 = jug.WaterJugAction(jug.ActionType.POUR, jug.Jug.A)
    state2 = state1.apply_action(action2)
    print(action2)
    print(state2)

def hash():
    world = jug.WaterJugWorld(5, 3)
    start = jug.WaterJugState(world, 2, 3)
    goal = jug.WaterJugState(world, 4, 1)
    action2 = jug.WaterJugAction(jug.ActionType.POUR, jug.Jug.A)
    print(start.__hash__())
    print(goal.__hash__())
    state2 = goal.apply_action(action2)
    print(state2.__hash__())

if __name__ == "__main__":
    # state_str()
    action()
    # hash()
