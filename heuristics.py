from model import State

def recovery_heuristic(state: State) -> float:
    """
    Admissible heuristic estimating remaining cost to reach Not At-Risk goal.
    Goal: risk_score <= threshold AND missing_submissions == 0.
    
    The heuristic considers:
    1. Cost to clear missing submissions: Each submission takes at least 1 action (SubmitAssignment) with cost 5.0.
    2. Cost to improve quiz score: Each PracticeQuiz adds 3.0 to score with cost 1.5.
    
    To be admissible, it must never overestimate the actual cost.
    """
    # Minimum cost to clear missing submissions
    submission_cost = state.missing_submissions * 5.0
    
    # We could add more components, but keeping it simple ensures admissibility.
    # For example, if risk score is still too high, we'd need more actions.
    # But those actions would also take time/days, which are limited.
    
    return float(submission_cost)
