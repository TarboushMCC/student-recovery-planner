from model import State, Action
from typing import Dict, Any

def _max_study_actions_per_day(constraints: Dict[str, Any]) -> int:
    legacy_value = constraints.get("max_study_hours", 8)
    configured = constraints.get("max_study_actions_per_day", legacy_value)
    return max(1, int(configured))

class AttendClass(Action):
    def __init__(self):
        super().__init__("Attend_Class", cost=2.0, description="Attend a lecture to improve attendance and understanding.")

    def is_applicable(self, state: State, constraints: Dict[str, Any]) -> bool:
        return state.days_to_deadline > 0 and state.fatigue < 8.0

    def apply(self, state: State) -> State:
        return State(
            attendance_rate=min(100.0, state.attendance_rate + 2.0),
            missing_submissions=state.missing_submissions,
            avg_quiz_score=min(100.0, state.avg_quiz_score + 0.5),
            lms_activity=min(100.0, state.lms_activity + 1.0),
            study_hours_per_week=state.study_hours_per_week,
            days_to_deadline=state.days_to_deadline - 1,
            fatigue=state.fatigue + 1.0,
            study_actions_today=0
        )

class StudyOneHour(Action):
    def __init__(self):
        super().__init__("Study_1_Hour", cost=1.0, description="Focused study session.")

    def is_applicable(self, state: State, constraints: Dict[str, Any]) -> bool:
        max_study_actions = _max_study_actions_per_day(constraints)
        return (
            state.fatigue < 9.0
            and state.days_to_deadline > 0
            and state.study_actions_today < max_study_actions
        )

    def apply(self, state: State) -> State:
        return State(
            attendance_rate=state.attendance_rate,
            missing_submissions=state.missing_submissions,
            avg_quiz_score=min(100.0, state.avg_quiz_score + 1.5),
            lms_activity=min(100.0, state.lms_activity + 2.0),
            study_hours_per_week=state.study_hours_per_week + 1.0,
            days_to_deadline=state.days_to_deadline, # Study doesn't necessarily consume a whole day in this model unless we say so
            fatigue=state.fatigue + 1.5,
            study_actions_today=state.study_actions_today + 1
        )

class SubmitAssignment(Action):
    def __init__(self):
        super().__init__("Submit_Assignment", cost=5.0, description="Complete and submit a missing assignment.")

    def is_applicable(self, state: State, constraints: Dict[str, Any]) -> bool:
        return state.missing_submissions > 0 and state.days_to_deadline > 0 and state.fatigue < 7.0

    def apply(self, state: State) -> State:
        return State(
            attendance_rate=state.attendance_rate,
            missing_submissions=state.missing_submissions - 1,
            avg_quiz_score=state.avg_quiz_score,
            lms_activity=min(100.0, state.lms_activity + 5.0),
            study_hours_per_week=state.study_hours_per_week,
            days_to_deadline=state.days_to_deadline - 1,
            fatigue=state.fatigue + 3.0,
            study_actions_today=0
        )

class PracticeQuiz(Action):
    def __init__(self):
        super().__init__("Practice_Quiz", cost=1.5, description="Take practice quizzes to improve quiz scores.")

    def is_applicable(self, state: State, constraints: Dict[str, Any]) -> bool:
        max_study_actions = _max_study_actions_per_day(constraints)
        return (
            state.fatigue < 8.5
            and state.days_to_deadline > 0
            and state.study_actions_today < max_study_actions
        )

    def apply(self, state: State) -> State:
        return State(
            attendance_rate=state.attendance_rate,
            missing_submissions=state.missing_submissions,
            avg_quiz_score=min(100.0, state.avg_quiz_score + 3.0),
            lms_activity=min(100.0, state.lms_activity + 3.0),
            study_hours_per_week=state.study_hours_per_week + 0.5,
            days_to_deadline=state.days_to_deadline,
            fatigue=state.fatigue + 2.0,
            study_actions_today=state.study_actions_today + 1
        )

class MeetTutor(Action):
    def __init__(self):
        super().__init__("Meet_Tutor", cost=3.0, description="Get help from a tutor.")

    def is_applicable(self, state: State, constraints: Dict[str, Any]) -> bool:
        # Check if tutor is available from constraints
        tutor_available = constraints.get("tutor_available", True)
        return tutor_available and state.days_to_deadline > 0 and state.fatigue < 9.0

    def apply(self, state: State) -> State:
        return State(
            attendance_rate=state.attendance_rate,
            missing_submissions=state.missing_submissions,
            avg_quiz_score=min(100.0, state.avg_quiz_score + 5.0),
            lms_activity=min(100.0, state.lms_activity + 2.0),
            study_hours_per_week=state.study_hours_per_week,
            days_to_deadline=state.days_to_deadline - 1,
            fatigue=state.fatigue + 1.0, # Tutors make it easier
            study_actions_today=0
        )

class Rest(Action):
    def __init__(self):
        super().__init__("Rest", cost=0.5, description="Take a break to reduce fatigue.")

    def is_applicable(self, state: State, constraints: Dict[str, Any]) -> bool:
        return state.fatigue > 0 and state.days_to_deadline > 0

    def apply(self, state: State) -> State:
        return State(
            attendance_rate=state.attendance_rate,
            missing_submissions=state.missing_submissions,
            avg_quiz_score=state.avg_quiz_score,
            lms_activity=state.lms_activity,
            study_hours_per_week=state.study_hours_per_week,
            days_to_deadline=state.days_to_deadline - 1,
            fatigue=max(0.0, state.fatigue - 4.0),
            study_actions_today=0
        )

def get_all_actions():
    return [AttendClass(), StudyOneHour(), SubmitAssignment(), PracticeQuiz(), MeetTutor(), Rest()]
