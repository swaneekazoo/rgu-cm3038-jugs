"""
Water Jug Problem Solver
Author: Adam Weir
"""

import cm3038.search as search
import cm3038.informed.search as informed
import enum


class ActionType(enum.Enum):
    """
    Represents the 3 types of ``Action`` described by the problem and their accompanying costs (per litre).
    Fill: Fill a jug from the tap.
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
    """Given one ``Jug``, return the other."""

    return {
        Jug.A: Jug.B,
        Jug.B: Jug.A
    }[jug]


class WaterJugWorld:
    """Models the problem's constants, in this case the capacities of the jugs."""

    def __init__(self, a_max: int, b_max: int):
        self.a_max = a_max
        self.b_max = b_max


class WaterJugAction(search.Action):
    """Models an ``Action`` in terms of its ``ActionType`` and which ``Jug`` to apply it to."""

    def __init__(self, action_type: ActionType, jug: Jug):
        super().__init__()
        self.action_type = action_type
        self.jug = jug

    def __str__(self):
        return {
            ActionType.FILL: "Fill Jug {} from the tap. Cost: {}".format(self.jug.value, self.cost),
            ActionType.POUR: "Pour Jug {} into Jug {}. Cost: {}".format(self.jug.value, other_jug(self.jug).value, self.cost),
            ActionType.EMPTY: "Empty Jug {} into the sink. Cost: {}".format(self.jug.value, self.cost)
        }[self.action_type]


class WaterJugState(search.State):
    """Models a ``State`` in terms of the volumes of the jugs."""

    def __init__(self, world: WaterJugWorld, a: int, b: int):
        self.world = world
        self.a = a
        self.b = b

    def __str__(self):
        return "Jug A: {}/{}l \n" \
               "Jug B: {}/{}l \n".format(self.a, self.world.a_max,
                                         self.b, self.world.b_max)

    def __eq__(self, other):
        if not isinstance(other, WaterJugState):
            return False
        return self.a == other.a and self.b == other.b

    def __hash__(self):
        return self.a + self.b * 100

    def apply_action(self, action: WaterJugAction):
        """Return the result of a given ``WaterJugAction`` on this ``WaterJugState``."""
        # Variables
        jug = action.jug
        action_type = action.action_type
        # Logic
        a, b = {
            ActionType.FILL: self.fill_result(jug),
            ActionType.POUR: self.pour_result(jug),
            ActionType.EMPTY: self.empty_result(jug)
        }[action_type]
        return WaterJugState(self.world, a, b)

    def successor(self):
        """Return a list of ``ActionStatePair``,
         representing every possible ``WaterJugAction`` that can be performed on this ``WaterJugState``."""
        result = []
        # Iterate over all Actions
        # If Action is possible, find its cost & add to result list
        for action_type in ActionType:
            for jug in Jug:
                action = WaterJugAction(action_type, jug)
                if self.is_possible(action):
                    action.cost = self.action_cost(action)
                    result.append(search.ActionStatePair(action, self.apply_action(action)))
        return result

    def get_volume(self, jug: Jug):
        """Return the volume of a given ``Jug``."""
        return {
            Jug.A: self.a,
            Jug.B: self.b
        }[jug]

    def get_capacity(self, jug: Jug):
        """Return the capacity of a given ``Jug``."""
        return {
            Jug.A: self.world.a_max,
            Jug.B: self.world.b_max
        }[jug]

    def is_full(self, jug: Jug):
        """Return ``True`` if a given ``Jug`` is full."""
        return {
            Jug.A: (self.a == self.world.a_max),
            Jug.B: (self.b == self.world.b_max)
        }[jug]

    def is_empty(self, jug: Jug):
        """Return ``True`` if a given ``Jug`` is empty."""
        return {
            Jug.A: (self.a == 0),
            Jug.B: (self.b == 0)
        }[jug]

    def set_volume_result(self, jug: Jug, volume: int):
        """Return the volumes of both jugs after setting a given ``Jug`` to a given ``volume``."""
        if volume <= self.get_capacity(jug):
            a, b = {
                Jug.A: (volume, self.b),
                Jug.B: (self.a, volume)
            }[jug]
            return a, b

    def fill_result(self, jug: Jug):
        """Return the volumes of both jugs after filling a given ``Jug``."""
        return self.set_volume_result(jug, self.get_capacity(jug))

    def pour_result(self, jug: Jug):
        """Return the volumes of both jugs after pouring a given ``Jug`` into the other."""
        # Variables
        other = other_jug(jug)
        volume = self.get_volume(jug)
        other_volume = self.get_volume(other)
        other_capacity = self.get_capacity(other)
        # Logic
        # If the jug can be emptied into the other without overflowing:
        if volume + other_volume <= other_capacity:
            # Pouring jug = 0. Receiving jug = volume of this jug + volume of the other
            a, b = {
                Jug.A: (0, volume + other_volume),
                Jug.B: (volume + other_volume, 0)
            }[jug]
        # If the jug cannot be emptied into the other without overflowing:
        else:
            # Pouring jug = its volume - the remaining capacity of the other. Receiving jug = its capacity
            a, b = {
                Jug.A: (volume - (other_capacity - other_volume), other_capacity),
                Jug.B: (other_capacity, volume - (other_capacity - other_volume))
            }[jug]
        return a, b

    def empty_result(self, jug: Jug):
        """Return the volumes of both jugs after emptying a given jug."""
        return self.set_volume_result(jug, 0)

    def is_possible(self, action: WaterJugAction):
        """Return ``True`` if a given ``WaterJugAction`` is possible."""
        # Variables
        action_type = action.action_type
        jug = action.jug
        # Logic
        return {
            # If this jug is full, you can't fill it
            ActionType.FILL: not self.is_full(jug),
            # If this jug is empty, you can't pour from it
            # If the other jug is full, you can't pour into it
            ActionType.POUR: not self.is_empty(jug) and not self.is_full(other_jug(jug)),
            # If this jug is empty, you can't empty it
            ActionType.EMPTY: not self.is_empty(action.jug)
        }[action_type]

    def action_cost(self, action: WaterJugAction):
        """Return the cost of a given ``WaterJugAction`` if performed on this ``WaterJugState``."""
        # Variables
        jug = action.jug
        volume = self.get_volume(jug)
        capacity = self.get_capacity(jug)
        other = other_jug(jug)
        other_volume = self.get_volume(other)
        other_capacity = self.get_capacity(other)
        action_type = action.action_type
        multiplier = action_type.value
        litres = 0
        # Logic
        if action_type == ActionType.FILL:
            litres = capacity - volume
        if action_type == ActionType.POUR:
            # If the jug can be emptied into the other without overflowing:
            if (volume + other_volume) <= other_capacity:
                litres = volume
            else:
                litres = other_capacity - other_volume
        if action_type == ActionType.EMPTY:
            litres = volume
        return litres * multiplier


class WaterJugSearchProblemBFS(search.SearchProblem):
    """
    A domain-dependent uninformed SearchProblem for the Water Jug Problem.
    This implementation uses Breadth-First Search.
    """

    def __init__(self, start: WaterJugState, goal: WaterJugState):
        super().__init__(start)
        self.start = start
        self.goal = goal

    def __str__(self):
        start_a = self.start.a
        start_b = self.start.b
        goal_a = self.goal.a
        goal_b = self.goal.b
        a_max = self.start.world.a_max
        b_max = self.start.world.b_max
        return "Problem: \n" \
               "Jug A: {}/{}l, Jug B: {}/{}l -> Jug A: {}/{}l, Jug B: {}/{}l \n".format(start_a, a_max,
                                                                                                 start_b, b_max,
                                                                                                 goal_a, a_max,
                                                                                                 goal_b, b_max)

    def isGoal(self, state: WaterJugState):
        return state == self.goal


class WaterJugSearchProblemDFS(search.SearchProblem):
    """
    A domain-dependent uninformed SearchProblem for the Water Jug Problem.
    This implementation uses Breadth-First Search.
    """

    def __init__(self, start: WaterJugState, goal: WaterJugState):
        super().__init__(start)
        self.start = start
        self.goal = goal

    def __str__(self):
        start_a = self.start.a
        start_b = self.start.b
        goal_a = self.goal.a
        goal_b = self.goal.b
        a_max = self.start.world.a_max
        b_max = self.start.world.b_max
        return "Problem: \n" \
               "Jug A: {}/{}l, Jug B: {}/{}l -> Jug A: {}/{}l, Jug B: {}/{}l \n".format(start_a, a_max,
                                                                                        start_b, b_max,
                                                                                        goal_a, a_max,
                                                                                        goal_b, b_max)

    def isGoal(self, state: WaterJugState):
        return state == self.goal

    def addChild(self, fringe, childNode):
        fringe.insert(0, childNode)


class GBFSearchProblem(informed.BestFirstSearchProblem):
    """A domain-independent informed SearchProblem.
    This abstract class uses Greedy Best-First Search."""

    def __init__(self, start, goal):
        super().__init__(start, goal)

    def evaluation(self, node):
        """Return the result of the A* evaluation function f(n) = g(n) + h(n)."""
        return self.heuristic(node.state)

    def heuristic(self, state):
        """Return the result of the heuristic function h(n)."""
        pass


class AStarSearchProblem(informed.BestFirstSearchProblem):
    """A domain-independent informed SearchProblem.
    This abstract class uses A* Search."""

    def __init__(self, start, goal):
        super().__init__(start, goal)

    def evaluation(self, node):
        """Return the result of the A* evaluation function f(n) = g(n) + h(n)."""
        return node.getCost() + self.heuristic(node.state)

    def heuristic(self, state):
        """Return the result of the heuristic function h(n)."""
        pass


class WaterJugSearchProblemGBF(GBFSearchProblem):
    """
    A domain-dependent informed SearchProblem for the Water Jug Problem.
    This implementation uses Greedy Best-First Search with the 'Markings' heuristic.
    """

    def __init__(self, start: WaterJugState, goal: WaterJugState):
        super().__init__(start, goal)
        self.start = start
        self.goal = goal

    def __str__(self):
        start_a = self.start.a
        start_b = self.start.b
        goal_a = self.goal.a
        goal_b = self.goal.b
        a_max = self.start.world.a_max
        b_max = self.start.world.b_max
        return "Problem: \n" \
               "Jug A: {}/{}l, Jug B: {}/{}l -> Jug A: {}/{}l, Jug B: {}/{}l \n".format(start_a, a_max,
                                                                                        start_b, b_max,
                                                                                        goal_a, a_max,
                                                                                        goal_b, b_max)

    def isGoal(self, state: WaterJugState):
        return state == self.goal

    def heuristic(self, state: WaterJugState):
        """Return the result of the 'Markings' heuristic function h(n), where n is a given ``WaterJugState``."""
        result = 0.0
        deficit = 0
        excess = 0
        # 1.) Difference
        a_diff = abs(self.goal.a - state.a)
        b_diff = abs(self.goal.b - state.b)
        total_difference = a_diff + b_diff
        max_difference = max(a_diff, b_diff)
        # 2.) Deficit/Excess
        total = state.a + state.b
        goal_total = self.goal.a + self.goal.b
        pourable = 0
        # If there is a deficit:
        if total < goal_total:
            deficit = goal_total - total
            # If any of the difference can be resolved by using the POUR action:
            if total_difference > deficit:
                pourable = max_difference - deficit
        # If there is an excess:
        elif total > goal_total:
            excess = total - goal_total
            # If any of the difference can be resolved by using the POUR action:
            if total_difference > excess:
                pourable = max_difference - excess
        # If there is no deficit or excess:
        else:
            pourable = max_difference
        # 3.) Sum & return
        result += deficit * ActionType.FILL.value
        result += pourable * ActionType.POUR.value
        result += excess * ActionType.EMPTY.value
        return result


class WaterJugSearchProblemAStar(AStarSearchProblem):
    """
    A domain-dependent informed SearchProblem for the Water Jug Problem.
    This implementation uses A* Search with the 'Markings' heuristic.
    """

    def __init__(self, start: WaterJugState, goal: WaterJugState):
        super().__init__(start, goal)
        self.start = start
        self.goal = goal

    def __str__(self):
        start_a = self.start.a
        start_b = self.start.b
        goal_a = self.goal.a
        goal_b = self.goal.b
        a_max = self.start.world.a_max
        b_max = self.start.world.b_max
        return "Problem: \n" \
               "Jug A: {}/{}l, Jug B: {}/{}l -> Jug A: {}/{}l, Jug B: {}/{}l \n".format(start_a, a_max,
                                                                                        start_b, b_max,
                                                                                        goal_a, a_max,
                                                                                        goal_b, b_max)

    def isGoal(self, state: WaterJugState):
        return state == self.goal

    def heuristic(self, state: WaterJugState):
        """Return the result of the 'Markings' heuristic function h(n), where n is a given ``WaterJugState``."""
        result = 0.0
        deficit = 0
        excess = 0
        # 1.) Difference
        a_diff = abs(self.goal.a - state.a)
        b_diff = abs(self.goal.b - state.b)
        total_difference = a_diff + b_diff
        max_difference = max(a_diff, b_diff)
        # 2.) Deficit/Excess
        total = state.a + state.b
        goal_total = self.goal.a + self.goal.b
        pourable = 0
        # If there is a deficit:
        if total < goal_total:
            deficit = goal_total - total
            # If any of the difference can be resolved by using the POUR action:
            if total_difference > deficit:
                pourable = max_difference - deficit
        # If there is an excess:
        elif total > goal_total:
            excess = total - goal_total
            # If any of the difference can be resolved by using the POUR action:
            if total_difference > excess:
                pourable = max_difference - excess
        # If there is no deficit or excess:
        else:
            pourable = max_difference
        # 3.) Sum & return
        result += deficit * ActionType.FILL.value
        result += pourable * ActionType.POUR.value
        result += excess * ActionType.EMPTY.value
        return result


class JugOverflowException(Exception):
    """A custom ``Exception`` to prevent the user-input jug volume parameters from exceeding the jug capacities."""

    def __init__(self):
        super().__init__()


class JugUnderflowException(Exception):
    """A custom ``Exception`` to prevent the user-input parameters from being set to < 0."""

    def __init__(self):
        super().__init__()


def run():
    # Get user input
    invalid = True
    while invalid:
        try:
            print("Capacity for Jug A: ")
            a_max = int(input())
            print("Capacity for Jug B: ")
            b_max = int(input())
            print("Starting volume for Jug A: ")
            a = int(input())
            print("Starting volume for Jug B: ")
            b = int(input())
            print("Goal volume for Jug A: ")
            a_goal = int(input())
            print("Goal volume for Jug B: ")
            b_goal = int(input())
            if a > a_max or b > b_max or a_goal > a_max or b_goal > b_max:
                raise JugOverflowException
            if a_max < 0 or b_max < 0 or a < 0 or b < 0 or a_goal < 0 or b_goal < 0:
                raise JugUnderflowException
            invalid = False
        except JugOverflowException:
            print("Please enter starting and goal volumes for both jugs which are less than their capacities.")
        except JugUnderflowException:
            print("Please enter numbers greater than 0 only.")
        except ValueError:
            print("Please enter numbers only.")
    # Set up problem
    world = WaterJugWorld(a_max, b_max)
    initial_state = WaterJugState(world, a, b)
    goal_state = WaterJugState(world, a_goal, b_goal)
    # problem = WaterJugSearchProblemBFS(initial_state, goal_state)
    # problem = WaterJugSearchProblemDFS(initial_state, goal_state)
    # problem = WaterJugSearchProblemGreedy(initial_state, goal_state)
    problem = WaterJugSearchProblemAStar(initial_state, goal_state)
    # Search & print
    path = problem.search()
    print("Done!\n")
    print(problem)
    if path is None:
        print("No solution.")
    else:
        print(path)
        print("Nodes visited: {}\n".format(problem.nodeVisited))
        print("Cost: {}\n".format(path.cost))


if __name__ == "__main__":
    run()
