import streamlit as st
import pandas as pd
import plotly.express as px

from model import State
from astar import astar_search, greedy_search
from actions import get_all_actions
from heuristics import recovery_heuristic
from utils import load_student_data, generate_synthetic_data, row_to_state


st.set_page_config(page_title="Student At-Risk Recovery Planner", layout="wide")

st.title("Student At-Risk Recovery Planner")
st.markdown(
    "A* planning dashboard for moving a student from **At-Risk** to **Not At-Risk** "
    "with minimum weighted effort."
)

if "df" not in st.session_state:
    st.session_state.df = None


def build_constraints(
    tutor_available: bool,
    max_study_actions_per_day: int,
    max_plan_steps: int,
    deadline_weight: float,
    fatigue_weight: float,
) -> dict:
    return {
        "tutor_available": tutor_available,
        "max_study_actions_per_day": max_study_actions_per_day,
        "max_plan_steps": max_plan_steps,
        "deadline_weight": deadline_weight,
        "fatigue_weight": fatigue_weight,
    }


def clear_results():
    st.session_state.pop("astar_result", None)
    st.session_state.pop("greedy_result", None)


def build_plan_table(initial_state: State, plan, constraints: dict) -> pd.DataFrame:
    rows = []
    current_state = initial_state
    for i, (action, next_state) in enumerate(plan, start=1):
        step_cost = action.get_cost(current_state, constraints)
        rows.append(
            {
                "Step": i,
                "Action": action.name,
                "Step Cost": round(step_cost, 2),
                "Risk Score": round(next_state.calculate_risk_score(), 2),
                "Missing": int(next_state.missing_submissions),
                "Fatigue": round(next_state.fatigue, 1),
            }
        )
        current_state = next_state
    return pd.DataFrame(rows)


st.sidebar.header("Constraints / Settings")
risk_threshold = st.sidebar.slider("Risk threshold (goal)", 0.0, 1.0, 0.2, 0.01)
max_plan_steps = st.sidebar.number_input("Max plan steps", min_value=1, max_value=30, value=12, step=1)
max_study_actions_per_day = st.sidebar.number_input(
    "Max study actions per day", min_value=1, max_value=10, value=3, step=1
)
tutor_available = st.sidebar.checkbox("Tutor available", value=True)
st.sidebar.markdown("**Cost weights**")
deadline_weight = st.sidebar.slider("Deadline", 0.0, 5.0, 1.0, 0.1)
fatigue_weight = st.sidebar.slider("Fatigue", 0.0, 5.0, 1.0, 0.1)

constraints = build_constraints(
    tutor_available=tutor_available,
    max_study_actions_per_day=int(max_study_actions_per_day),
    max_plan_steps=int(max_plan_steps),
    deadline_weight=float(deadline_weight),
    fatigue_weight=float(fatigue_weight),
)

st.header("1. Student Input")
input_mode = st.radio(
    "Choose assessment mode",
    ["CSV / Synthetic Student List", "Assess One Student (Custom Fields)"],
    horizontal=True,
)

initial_state = None
student_label = None

if input_mode == "CSV / Synthetic Student List":
    uploaded_file = st.file_uploader("Upload Student CSV", type="csv")

    col1, col2 = st.columns(2)
    with col1:
        if uploaded_file is not None:
            st.session_state.df = load_student_data(uploaded_file)
            clear_results()
            st.success("CSV uploaded.")
    with col2:
        if st.button("Generate Synthetic Scenarios"):
            st.session_state.df = generate_synthetic_data()
            clear_results()
            st.info("Synthetic scenarios generated.")

    if st.session_state.df is not None and not st.session_state.df.empty:
        st.subheader("Student List")
        st.dataframe(st.session_state.df, use_container_width=True)

        student_ids = st.session_state.df["student_id"].astype(str).tolist()
        selected_id = st.selectbox("Student", student_ids)
        student_row = st.session_state.df[st.session_state.df["student_id"].astype(str) == selected_id].iloc[0]
        initial_state = row_to_state(student_row)
        student_label = selected_id
else:
    st.subheader("Custom Fields for One Student Assessment")
    c1, c2, c3 = st.columns(3)
    with c1:
        custom_student_id = st.text_input("Student ID", value="CUSTOM_001")
        attendance_rate = st.number_input("Attendance rate (0-100)", 0.0, 100.0, 76.0, 0.1)
        missing_submissions = st.number_input("Missing submissions (0-8)", 0, 8, 3, 1)
    with c2:
        avg_quiz_score = st.number_input("Avg quiz score (0-100)", 0.0, 100.0, 64.0, 0.1)
        lms_activity = st.number_input("LMS activity (0-100)", 0.0, 100.0, 67.0, 0.1)
        days_to_deadline = st.number_input("Days to deadline (0-14)", 0, 30, 4, 1)
    with c3:
        study_hours_per_week = st.number_input("Study hours per week", 0.0, 40.0, 6.0, 0.5)
        fatigue = st.number_input("Initial fatigue (0-10)", 0.0, 10.0, 2.0, 0.1)

    initial_state = State(
        attendance_rate=float(attendance_rate),
        missing_submissions=int(missing_submissions),
        avg_quiz_score=float(avg_quiz_score),
        lms_activity=float(lms_activity),
        study_hours_per_week=float(study_hours_per_week),
        days_to_deadline=int(days_to_deadline),
        fatigue=float(fatigue),
        study_actions_today=0,
    )
    student_label = custom_student_id.strip() or "CUSTOM_001"

if initial_state is None:
    st.info("Upload a CSV, generate scenarios, or fill custom fields to start.")
    st.stop()

active_signature = (
    student_label,
    initial_state,
    risk_threshold,
    max_plan_steps,
    max_study_actions_per_day,
    tutor_available,
    deadline_weight,
    fatigue_weight,
)
if st.session_state.get("active_signature") != active_signature:
    st.session_state["active_signature"] = active_signature
    clear_results()

st.subheader(f"Initial State: {student_label}")
initial_risk = initial_state.calculate_risk_score()
initial_status = "At-Risk" if (initial_risk > risk_threshold or initial_state.missing_submissions > 0) else "Not At-Risk"

initial_summary = pd.DataFrame(
    [
        {
            "attendance": initial_state.attendance_rate,
            "missing": initial_state.missing_submissions,
            "quiz": initial_state.avg_quiz_score,
            "lms": initial_state.lms_activity,
            "study_hours": initial_state.study_hours_per_week,
            "days_to_deadline": initial_state.days_to_deadline,
            "fatigue": initial_state.fatigue,
            "risk_score": round(initial_risk, 2),
            "status": initial_status,
        }
    ]
)
st.dataframe(initial_summary, use_container_width=True, hide_index=True)

st.header("2. Planning")
actions = get_all_actions()
p1, p2 = st.columns(2)

with p1:
    if st.button("Run A*"):
        with st.spinner("Running A* search..."):
            plan, expanded, duration, total_cost = astar_search(
                initial_state,
                actions,
                recovery_heuristic,
                lambda s: s.is_goal(risk_threshold),
                constraints,
            )
            st.session_state["astar_result"] = {
                "plan": plan,
                "expanded": expanded,
                "duration": duration,
                "total_cost": total_cost,
            }
        st.success("A* completed.")

with p2:
    if st.button("Run Greedy (Baseline)"):
        with st.spinner("Running greedy baseline..."):
            plan, expanded, duration, total_cost = greedy_search(
                initial_state,
                actions,
                recovery_heuristic,
                lambda s: s.is_goal(risk_threshold),
                constraints,
            )
            st.session_state["greedy_result"] = {
                "plan": plan,
                "expanded": expanded,
                "duration": duration,
                "total_cost": total_cost,
            }
        st.success("Greedy completed.")

if "astar_result" in st.session_state or "greedy_result" in st.session_state:
    st.header("3. Results")
    comparison_rows = []

    if "astar_result" in st.session_state:
        result = st.session_state["astar_result"]
        plan = result["plan"]
        if plan is not None:
            total_cost = result["total_cost"] if result["total_cost"] is not None else 0.0
            final_state = plan[-1][1] if plan else initial_state
            final_risk = final_state.calculate_risk_score()
            comparison_rows.append(
                {
                    "Method": "A*",
                    "Cost": round(total_cost, 2),
                    "Runtime (s)": round(result["duration"], 4),
                    "Nodes Expanded": result["expanded"],
                    "Plan Length": len(plan),
                }
            )

            st.subheader("A* Plan")
            if plan:
                st.table(build_plan_table(initial_state, plan, constraints))
            else:
                st.info("Student already satisfies the goal. No actions required.")

            vc1, vc2 = st.columns(2)
            with vc1:
                fig_risk = px.bar(
                    x=["Before", "After"],
                    y=[initial_risk, final_risk],
                    title="Risk (before/after)",
                    labels={"x": "Stage", "y": "Risk score"},
                )
                st.plotly_chart(fig_risk, use_container_width=True)

            with vc2:
                action_counts = {}
                for action, _ in plan:
                    action_counts[action.name] = action_counts.get(action.name, 0) + 1
                if action_counts:
                    fig_actions = px.bar(
                        x=list(action_counts.keys()),
                        y=list(action_counts.values()),
                        title="Action counts",
                        labels={"x": "Action", "y": "Count"},
                    )
                    st.plotly_chart(fig_actions, use_container_width=True)
                else:
                    st.info("No action counts to plot.")
        else:
            st.error("A* could not find a valid plan with current constraints.")

    if "greedy_result" in st.session_state:
        result = st.session_state["greedy_result"]
        plan = result["plan"]
        if plan is not None:
            total_cost = result["total_cost"] if result["total_cost"] is not None else 0.0
            comparison_rows.append(
                {
                    "Method": "Greedy",
                    "Cost": round(total_cost, 2),
                    "Runtime (s)": round(result["duration"], 4),
                    "Nodes Expanded": result["expanded"],
                    "Plan Length": len(plan),
                }
            )
        else:
            st.warning("Greedy could not find a valid plan with current constraints.")

    if comparison_rows:
        st.subheader("Method Comparison")
        st.table(pd.DataFrame(comparison_rows))

st.header("4. What-If Simulation")
st.markdown("Runs 3 required what-if cases from the selected student context.")

if st.button("Run 3 What-If Cases"):
    cases = [
        (
            "Deadline Closer",
            State(
                attendance_rate=initial_state.attendance_rate,
                missing_submissions=initial_state.missing_submissions,
                avg_quiz_score=initial_state.avg_quiz_score,
                lms_activity=initial_state.lms_activity,
                study_hours_per_week=initial_state.study_hours_per_week,
                days_to_deadline=max(1, initial_state.days_to_deadline - 2),
                fatigue=initial_state.fatigue,
                study_actions_today=0,
            ),
            {**constraints},
        ),
        (
            "Tutor Unavailable",
            initial_state,
            {**constraints, "tutor_available": False},
        ),
        (
            "High Initial Fatigue",
            State(
                attendance_rate=initial_state.attendance_rate,
                missing_submissions=initial_state.missing_submissions,
                avg_quiz_score=initial_state.avg_quiz_score,
                lms_activity=initial_state.lms_activity,
                study_hours_per_week=initial_state.study_hours_per_week,
                days_to_deadline=initial_state.days_to_deadline,
                fatigue=min(10.0, initial_state.fatigue + 3.0),
                study_actions_today=0,
            ),
            {**constraints},
        ),
    ]

    rows = []
    for case_name, case_state, case_constraints in cases:
        plan, expanded, duration, total_cost = astar_search(
            case_state,
            actions,
            recovery_heuristic,
            lambda s: s.is_goal(risk_threshold),
            case_constraints,
        )
        if plan is None:
            rows.append(
                {
                    "Case": case_name,
                    "Result": "No valid plan",
                    "Cost": "-",
                    "Final Risk": "-",
                    "Nodes Expanded": expanded,
                    "Runtime (s)": round(duration, 4),
                }
            )
            continue

        final_state = plan[-1][1] if plan else case_state
        rows.append(
            {
                "Case": case_name,
                "Result": "Plan found",
                "Cost": round(total_cost or 0.0, 2),
                "Final Risk": round(final_state.calculate_risk_score(), 2),
                "Nodes Expanded": expanded,
                "Runtime (s)": round(duration, 4),
            }
        )

    st.table(pd.DataFrame(rows))
