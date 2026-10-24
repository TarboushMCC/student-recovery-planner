# Student At-Risk Recovery Planner

This application helps students at risk of failing by generating personalized action plans using the **A* Search Algorithm**.

## Features
- **A* Search from Scratch**: Implementation of the A* algorithm including open/closed sets, g(n), h(n), and f(n).
- **Baseline Comparison**: Compare A* results with a Greedy search baseline.
- **Interactive Dashboard**: Built with Streamlit for data loading, parameter tuning, and visualization.
- **What-If Simulations**: Test how changes in deadlines, tutor availability, or fatigue affect the recovery plan.
- **Synthetic Data Generation**: Generate student scenarios for testing.

## Project Structure
- `app.py`: Main Streamlit application.
- `astar.py`: Implementation of A* and Greedy search algorithms.
- `model.py`: State representation and Action base class.
- `actions.py`: Concrete action definitions (Attend Class, Study, Submit Assignment, etc.).
- `heuristics.py`: Admissible heuristic function.
- `utils.py`: Data loading and synthetic data generation.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app.py
   ```

## Academic Integrity
This project was developed with the assistance of AI tools for code structure and implementation, as permitted by course guidelines.
