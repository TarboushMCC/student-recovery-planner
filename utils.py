import pandas as pd
import random
from model import State

def load_student_data(file_path: str):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def generate_synthetic_data(num_students: int = 10):
    data = []
    for i in range(num_students):
        data.append({
            "student_id": f"SYN{i+1:03d}",
            "attendance_rate": round(random.uniform(40, 95), 1),
            "missing_submissions": random.randint(0, 8),
            "avg_quiz_score": round(random.uniform(30, 90), 1),
            "lms_activity": round(random.uniform(10, 100), 1),
            "study_hours_per_week": round(random.uniform(0, 15), 1),
            "days_to_deadline": random.randint(1, 14)
        })
    return pd.DataFrame(data)

def row_to_state(row) -> State:
    fatigue = float(row["fatigue"]) if "fatigue" in row else 0.0
    study_actions_today = int(row["study_actions_today"]) if "study_actions_today" in row else 0
    return State(
        attendance_rate=row['attendance_rate'],
        missing_submissions=row['missing_submissions'],
        avg_quiz_score=row['avg_quiz_score'],
        lms_activity=row['lms_activity'],
        study_hours_per_week=row['study_hours_per_week'],
        days_to_deadline=row['days_to_deadline'],
        fatigue=fatigue,
        study_actions_today=study_actions_today
    )
