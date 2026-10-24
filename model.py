import dataclasses
from typing import Dict, Any, Optional

@dataclasses.dataclass(frozen=True)
class State:
    attendance_rate: float
    missing_submissions: int
    avg_quiz_score: float
    lms_activity: float
    study_hours_per_week: float
    days_to_deadline: int
    fatigue: float = 0.0
    study_actions_today: int = 0

    def calculate_risk_score(self) -> float:
        # Normalized risk score in [0, 1] to align with the project sample output style.
        risk_points = (
            (100 - self.attendance_rate) * 0.18 +
            (self.missing_submissions * 2.5) +
            (100 - self.avg_quiz_score) * 0.10 +
            (100 - self.lms_activity) * 0.06 +
            (max(0, 10 - self.study_hours_per_week) * 0.20) +
            (max(0, 7 - self.days_to_deadline) * 0.35) +
            (self.fatigue * 0.40)
        )
        risk = risk_points / 100.0
        return min(1.0, max(0.0, risk))

    def is_goal(self, threshold: float = 0.2) -> bool:
        return self.calculate_risk_score() <= threshold and self.missing_submissions == 0

    def __lt__(self, other):
        return False # Needed for heapq priority queue comparison tie-breaking

class Action:
    def __init__(self, name: str, cost: float, description: str):
        self.name = name
        self.cost = cost
        self.description = description

    def is_applicable(self, state: State, constraints: Dict[str, Any]) -> bool:
        raise NotImplementedError

    def apply(self, state: State) -> State:
        raise NotImplementedError

    def get_cost(self, state: State, constraints: Optional[Dict[str, Any]] = None) -> float:
        constraints = constraints or {}
        deadline_weight = float(constraints.get("deadline_weight", 1.0))
        fatigue_weight = float(constraints.get("fatigue_weight", 1.0))

        deadline_penalty = max(0.0, (7.0 - state.days_to_deadline) / 7.0)
        fatigue_penalty = max(0.0, state.fatigue / 10.0)

        return self.cost + (deadline_weight * deadline_penalty) + (fatigue_weight * fatigue_penalty)
