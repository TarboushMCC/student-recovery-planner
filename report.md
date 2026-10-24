# Student At-Risk Recovery Planner: Project Report

## 1. Problem Formulation
The "Student At-Risk Recovery Planner" is designed as a search problem to help students navigate academic difficulties. The goal is to move a student from an "At-Risk" state to a "Not At-Risk" state with minimal cost.

### State Representation
The state is represented by a set of academic and personal features:
- **Attendance Rate**: Percentage of classes attended.
- **Missing Submissions**: Number of pending assignments.
- **Average Quiz Score**: Current performance in assessments.
- **LMS Activity**: Engagement with the Learning Management System.
- **Study Hours per Week**: Time dedicated to self-study.
- **Days to Deadline**: Time remaining until critical milestones.
- **Fatigue**: A cumulative measure of student burnout (0 to 10).

### Actions and Transitions
Six actions are defined to modify the state:
1. **Attend Class**: Increases attendance and quiz score; increases fatigue.
2. **Study 1 Hour**: Increases quiz score and LMS activity; increases fatigue.
3. **Submit Assignment**: Reduces missing submissions; significantly increases fatigue.
4. **Practice Quiz**: Increases quiz score; moderate fatigue increase.
5. **Meet Tutor**: Increases quiz score; low fatigue increase.
6. **Rest**: Reduces fatigue; consumes time (days).

### Cost Model
Each action has a base cost representing effort/time. For example, `Submit_Assignment` has a high cost (5.0), while `Rest` has a low cost (0.5).

## 2. A* Algorithm and Heuristic
The core planning engine uses the A* search algorithm, implemented from scratch. It maintains an open set (priority queue) and a closed set to explore states efficiently.

### Heuristic Function: `h(n)`
The heuristic function estimates the remaining cost to reach the goal:
`h(n) = missing_submissions * 5.0`

**Admissibility Justification**: 
The goal requires `missing_submissions == 0`. The only action that reduces `missing_submissions` is `Submit_Assignment`, which has a cost of 5.0. Therefore, the minimum cost to reach the goal from a state with $N$ missing submissions is at least $5.0 \times N$. Since $h(n)$ never overestimates the actual cost, it is admissible.

## 3. Results and Comparison
The application compares A* search with a Greedy search baseline.

| Metric | A* Search | Greedy Search |
|--------|-----------|---------------|
| Optimality | Guaranteed | Not Guaranteed |
| Completeness | Yes | No (can loop) |
| Performance | Balanced | Faster but less reliable |

## 4. What-If Scenarios
The dashboard allows testing various constraints:
1. **Reduced Deadline**: Closer deadlines restrict the available actions and may make a recovery plan impossible.
2. **Tutor Unavailability**: Without a tutor, students must rely on higher-cost or higher-fatigue actions like self-study.
3. **High Initial Fatigue**: Starting with high fatigue forces the student to take `Rest` actions early, consuming valuable time.

## 5. AI Tool Acknowledgment
This project was developed with the assistance of Manus AI for initial code scaffolding, algorithm implementation guidance, and report structuring. All logic was verified and tested to ensure compliance with project requirements.
