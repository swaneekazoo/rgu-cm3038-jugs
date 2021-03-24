"""
Water Jug Problem Solver using A* Search
Author: Adam Weir
"""

import cm3038.search as search
import cm3038.informed.search as informed
import enum


class ActionType(enum.Enum):

    """
    Represents the 3 types of action described by the problem and their accompanying costs (per litre).
    Fill: Fill a jug from the sink.
    Pour: Pour from one jug to the other until the receiving jug is full or the pouring jug is empty.
    Empty: Empty a jug into the sink.
    """
    FILL = 5
    POUR = 1
    EMPTY = 20


class Jug(enum.Enum):

    """Represents the 2 jugs at the heart of the problem and their string representations."""
    A = 'A'
    B = 'B'

def other_jug(jug: Jug):
    """Given one jug, return the other."""

    return {
        Jug.A: Jug.B,
        Jug.B: Jug.A
    }[jug]

class WaterJugWorld:

    """Models the problem's constants, in this case the capacity of the jugs."""
    def __init__(self, a_max: int, b_max: int):
        self.a_max = a_max
        self.b_max = b_max


class WaterJugAction(search.Action):

    """Models an Action given its type and which jug to apply it to."""

    def __init__(self, action_type: ActionType, jug: Jug):
        super().__init__()
        self.action_type = action_type
        self.jug = jug
    def __str__(self):
        return {
            ActionType.FILL: "Fill Jug {} from the tap.".format(self.jug.value),
            ActionType.POUR: "Pour Jug {} into the other.".format(self.jug.value),
            ActionType.EMPTY: "Empty Jug {} into the sink.".format(self.jug.value)
        }[self.action_type]


class WaterJugState(search.State):
    """
    Models the current state, i.e. the volume in the jugs.
    Takes a reference to the 'world' for jug capacities.
    """

    def __init__(self, world: WaterJugWorld, a: int, b: int):
        self.world = world
        self.a = a
        self.b = b

    def __str__(self):
        return "Jug A: {}/{}l \n" \
               "Jug B: {}/{}l".format(self.a, self.world.a_max,
                                      self.b, self.world.b_max)

    def __eq__(self, other):
        if self.a == other.a and self.b == other.b:
            return True
        else:
            return False

    def __hash__(self):
        return self.a + self.b * 100

    def apply_action(self, action: WaterJugAction):
        # TODO
        """Return the result of a given Action on the current State."""

        jug = action.jug
        action_type = action.action_type
        a = 0
        b = 0
        a, b = {
            ActionType.FILL: self.fill(jug),
            ActionType.POUR: self.pour(jug),
            ActionType.EMPTY: {
                Jug.A: (0, self.b),
                Jug.B: (self.a, 0)
            }[jug]
        }[action_type]
        return WaterJugState(self.world, a, b)

    def successor(self):
        """Return a list of all possible action-state pairs from the current State."""

        result = []
        # Iterate over all ActionType/Jug combinations
        # Add to result if possible
        for action_type in ActionType:
            for jug in Jug:
                action = WaterJugAction(action_type, jug)
                possible = self.is_possible(action)
                if self.is_possible(action):
                    result.append(search.ActionStatePair(action, self.apply_action(action)))
        return result

    # Helper methods

    def get_volume(self, jug: Jug):
        """Return the volume of a given jug."""

        return {
            Jug.A: self.a,
            Jug.B: self.b
        }[jug]

    def set_volume(self, jug: Jug, volume: int):
        """Set the given jug's volume to the given volume."""

        if volume <= self.get_capacity(jug):
            self.a, self.b = {
                Jug.A: (volume, self.b),
                Jug.B: (self.a, volume)
            }[jug]
        else:
            print("Cannot exceed jug capacity.")

    def get_capacity(self, jug: Jug):
        """Return the capacity of a given jug."""

        return {
            Jug.A: self.world.a_max,
            Jug.B: self.world.b_max
        }[jug]

    def is_full(self, jug: Jug):
        """Return True if a given jug is full."""

        return {
            Jug.A: (self.a == self.world.a_max),
            Jug.B: (self.b == self.world.b_max)
        }[jug]

    def is_empty(self, jug: Jug):
        """Return True if a given jug is empty."""

        return {
            Jug.A: (self.a == 0),
            Jug.B: (self.b == 0)
        }[jug]


    def fill(self, jug: Jug):
        """Return a tuple (A, B) representing the volumes in the jugs after filling the given jug."""

        return {
            Jug.A: (self.world.a_max, self.b),
            Jug.B: (self.a, self.world.b_max)
        }[jug]

    def pour(self, jug: Jug):
        """Return a tuple (A, B) representing the volumes in the jugs after pouring the given jug into the other."""

        a = 0
        b = 0
        other = other_jug(jug)
        volume = self.get_volume(jug)
        other_volume = self.get_volume(other)
        capacity = self.get_capacity(jug)
        other_capacity = self.get_capacity(other)
        # If the jug can be emptied into the other without overflowing
        if self.a + self.b <= other_capacity:
            self.set_volume(jug, 0)
            self.set_volume(other, (volume + other_volume))
        else:
            self.set_volume(jug, volume - (other_capacity - other_volume))
            self.set_volume(other, other_capacity)


    def empty(self, jug: Jug):
        """Return a tuple (A, B) representing the volumes in the jugs after emptying the given jug."""

        return {
            Jug.A: (0, self.b),
            Jug.B: (self.a, 0)
        }[jug]

    def is_possible(self, action: WaterJugAction):
        """Return True if a given action is possible."""

        action_type = action.action_type
        jug = action.jug
        return {
            # If this jug is full, you can't fill it
            ActionType.FILL: not self.is_full(jug),
            # If this jug is empty, you can't pour from it
            # If the other jug is full, you can't pour into it
            ActionType.POUR: {
                Jug.A: not self.is_empty(Jug.A) and not self.is_full(Jug.B),
                Jug.B: not self.is_empty(Jug.B) and not self.is_full(Jug.A)
            }[jug],
            # If this jug is empty, you can't empty it
            ActionType.EMPTY: not self.is_empty(action.jug)
        }[action_type]


class AStarSearchProblem(informed.BestFirstSearchProblem):
    """A domain-independent informed SearchProblem, using A* Search."""

    def __init__(self, start, goal):
        super().__init__(start, goal)

    def evaluation(self, node):
        """Return the result of the A* evaluation function f(n) = g(n) + h(n)."""

        return node.getCost() + self.heuristic(node.state)

    def heuristic(self, state):
        """Return the result of the heuristic function h(n)."""

        pass


class WaterJugSearchProblem(search.SearchProblem):
    """A domain-dependent uninformed SearchProblem for the Water Jug Problem, using Breadth-First Search."""

    def __init__(self, start: WaterJugState, goal: WaterJugState):
        super().__init__(start)
        self.start = start
        self.goal = goal

    def isGoal(self, state: WaterJugState):
        return state == self.goal


class WaterJugSearchProblemAStar(AStarSearchProblem):
    """
    A domain-dependent informed SearchProblem for the Water Jug Problem, using A* Search.
    This implementation uses the 'Markings' heuristic.
    """

    def __init__(self, start: WaterJugState, goal: WaterJugState):
        super().__init__(start, goal)
        self.start = start
        self.goal = goal

    def isGoal(self, state: WaterJugState):
        return state == self.goal

    def heuristic(self, state: WaterJugState):
        """The Markings heuristic function."""

        result = 0.0
        # The total number of litres in both jugs
        total = state.a + state.b
        goal_total = self.goal.a + self.goal.b

        # Check whether the total amount of water needs to be increased or decreased
        # i.e., how much water, if any, needs to be filled from the tap or poured into the sink
        if total < goal_total:
            result += (goal_total - total) * 5.0
        elif total > goal_total:
            result += (total - goal_total) * 20.0
        if state.a < self.goal.a:
            result += self.goal.a - state.a
        elif state.b < self.goal.b:
            result += self.goal.b - state.b
        return abs(state.a - self.goal.a) + abs(state.b - self.goal.b)


def run():
    # invalid = True
    # while invalid:
    #     print("Capacity for Jug A: ")
    #     a_max = input()
    #     print("Capacity for Jug B: ")
    #     b_max = input()
    #     print("Starting volume for Jug A: ")
    #     a = input()
    #     print("Starting volume for Jug B: ")
    #     b = input()
    #     print("Goal volume for Jug A: ")
    #     a_goal = input()
    #     print("Goal volume for Jug B: ")
    #     b_goal = input()
    #     if a < a_max and b < b_max:
    #         invalid = False
    #     else:
    #         print("Invalid input. Please try again.")

    # TODO Validate & convert to int
    a_max = 5
    b_max = 3
    a = 0
    b = 0
    a_goal = 4
    b_goal = 0
    world = WaterJugWorld(a_max, b_max)
    initial_state = WaterJugState(world, a, b)
    goal_state = WaterJugState(world, a_goal, b_goal)
    problem = WaterJugSearchProblem(initial_state, goal_state)
    path = problem.search()
    print("Done!\n")
    if path is None:
        print("No solution.")  # no solution
    else:
        print(path)
        print("Nodes visited: {}\n".format(problem.nodeVisited))
        print("Cost: {}\n".format(path.cost))


if __name__ == "__main__":
    run()
