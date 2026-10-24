import heapq
import time
from typing import List, Tuple, Dict, Any, Optional, Callable
from model import State, Action

class Node:
    def __init__(
        self,
        state: State,
        parent=None,
        action: Optional[Action] = None,
        g: float = 0,
        h: float = 0,
        depth: int = 0,
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h
        self.f = g + h
        self.depth = depth

    def __lt__(self, other):
        return self.f < other.f

def astar_search(
    initial_state: State,
    actions: List[Action],
    heuristic_fn: Callable[[State], float],
    goal_fn: Callable[[State], bool],
    constraints: Dict[str, Any]
) -> Tuple[Optional[List[Tuple[Action, State]]], int, float, Optional[float]]:
    start_time = time.time()
    open_set = []
    closed_set = set()
    max_plan_steps = int(constraints.get("max_plan_steps", 12))
    max_nodes_expanded = int(constraints.get("max_nodes_expanded", 10000))
    
    start_node = Node(initial_state, g=0, h=heuristic_fn(initial_state))
    heapq.heappush(open_set, start_node)
    
    nodes_expanded = 0
    
    while open_set:
        current_node = heapq.heappop(open_set)
        
        if goal_fn(current_node.state):
            path = []
            node = current_node
            while node.parent:
                path.append((node.action, node.state))
                node = node.parent
            return path[::-1], nodes_expanded, time.time() - start_time, current_node.g
            
        if current_node.state in closed_set:
            continue
            
        closed_set.add(current_node.state)
        nodes_expanded += 1
        
        if nodes_expanded > max_nodes_expanded:
            break

        if current_node.depth >= max_plan_steps:
            continue

        for action in actions:
            if action.is_applicable(current_node.state, constraints):
                next_state = action.apply(current_node.state)
                next_depth = current_node.depth + 1
                if next_depth > max_plan_steps:
                    continue

                g_cost = current_node.g + action.get_cost(current_node.state, constraints)
                h_cost = heuristic_fn(next_state)
                next_node = Node(next_state, current_node, action, g_cost, h_cost, next_depth)
                heapq.heappush(open_set, next_node)
                
    return None, nodes_expanded, time.time() - start_time, None

def greedy_search(
    initial_state: State,
    actions: List[Action],
    heuristic_fn: Callable[[State], float],
    goal_fn: Callable[[State], bool],
    constraints: Dict[str, Any]
) -> Tuple[Optional[List[Tuple[Action, State]]], int, float, Optional[float]]:
    # Greedy picks action with best immediate heuristic improvement
    start_time = time.time()
    current_state = initial_state
    path = []
    nodes_expanded = 0
    visited = {initial_state}
    total_cost = 0.0
    max_plan_steps = int(constraints.get("max_plan_steps", 12))
    max_nodes_expanded = int(constraints.get("max_nodes_expanded", 1000))

    while not goal_fn(current_state):
        if len(path) >= max_plan_steps:
            return None, nodes_expanded, time.time() - start_time, None

        nodes_expanded += 1
        best_action = None
        best_next_state = None
        best_step_cost = 0.0
        min_h = float('inf')

        for action in actions:
            if action.is_applicable(current_state, constraints):
                next_state = action.apply(current_state)
                if next_state in visited:
                    continue
                h = heuristic_fn(next_state)
                if h < min_h:
                    min_h = h
                    best_action = action
                    best_next_state = next_state
                    best_step_cost = action.get_cost(current_state, constraints)
        
        if not best_action or nodes_expanded > max_nodes_expanded:
            return None, nodes_expanded, time.time() - start_time, None
            
        current_state = best_next_state
        visited.add(current_state)
        total_cost += best_step_cost
        path.append((best_action, current_state))
        
    return path, nodes_expanded, time.time() - start_time, total_cost
