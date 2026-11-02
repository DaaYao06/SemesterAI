import streamlit as st
import pandas as pd
from datetime import date, timedelta

# -----------------------------
# PAGE SETTINGS
# -----------------------------
st.set_page_config(
    page_title="SemesterAI",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------
# APP DATA
# -----------------------------
if "assignments" not in st.session_state:
    st.session_state.assignments = []

# -----------------------------
# TITLE
# -----------------------------
st.title("SemesterAI 🎓")
st.write("Your intelligent semester planning assistant.")

st.divider()

# -----------------------------
# DASHBOARD
# -----------------------------
st.header("📊 Dashboard")

assignments = st.session_state.assignments

total_assignments = len(assignments)
total_hours = sum(item["Estimated Hours"] for item in assignments)

if assignments:
    upcoming = [
        item for item in assignments
        if item["Due Date"] >= date.today()
    ]

    if upcoming:
        next_assignment = min(
            upcoming,
            key=lambda x: x["Due Date"]
        )

        next_deadline = (
            f'{next_assignment["Course"]} - '
            f'{next_assignment["Assignment"]} '
            f'({next_assignment["Due Date"]})'
        )
    else:
        next_deadline = "No upcoming deadlines"
else:
    next_deadline = "No assignments yet"

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Assignments", total_assignments)

with col2:
    st.metric("Total Study Hours", total_hours)

with col3:
    st.metric("Next Deadline", next_deadline)

st.divider()

# -----------------------------
# ADD ASSIGNMENT
# -----------------------------
st.header("➕ Add an Assignment")

with st.form("assignment_form", clear_on_submit=True):

    course = st.text_input(
        "Course Name",
        placeholder="Example: MAT 22A"
    )

    assignment = st.text_input(
        "Assignment Name",
        placeholder="Example: Homework 1"
    )

    due_date = st.date_input(
        "Due Date",
        min_value=date.today()
    )

    estimated_hours = st.number_input(
        "Estimated Hours",
        min_value=1,
        max_value=100,
        value=2
    )

    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High"]
    )

    submitted = st.form_submit_button(
        "Add Assignment",
        use_container_width=True
    )

if submitted:

    if not course.strip():
        st.error("Please enter a course name.")

    elif not assignment.strip():
        st.error("Please enter an assignment name.")

    else:

        new_assignment = {
            "Course": course.strip(),
            "Assignment": assignment.strip(),
            "Due Date": due_date,
            "Estimated Hours": estimated_hours,
            "Priority": priority
        }

        st.session_state.assignments.append(new_assignment)

        st.success("Assignment added successfully!")

        st.rerun()

st.divider()

# -----------------------------
# ASSIGNMENT LIST
# -----------------------------
st.header("📚 My Assignments")

if not st.session_state.assignments:

    st.info(
        "No assignments yet. Add your first assignment above."
    )

else:

    sorted_assignments = sorted(
        st.session_state.assignments,
        key=lambda x: x["Due Date"]
    )

    for index, item in enumerate(sorted_assignments):

        days_left = (item["Due Date"] - date.today()).days

        with st.container(border=True):

            col1, col2 = st.columns([5, 1])

            with col1:

                st.subheader(
                    f'{item["Course"]} — {item["Assignment"]}'
                )

                st.write(
                    f'📅 Due: {item["Due Date"].strftime("%B %d, %Y")}'
                )

                st.write(
                    f'⏱ Estimated time: {item["Estimated Hours"]} hours'
                )

                st.write(
                    f'🚩 Priority: {item["Priority"]}'
                )

                if days_left == 0:
                    st.warning("Due today!")

                elif days_left == 1:
                    st.warning("1 day remaining")

                elif days_left > 1:
                    st.write(
                        f"⏳ {days_left} days remaining"
                    )

                else:
                    st.error("Past due")

            with col2:

                if st.button(
                    "Delete",
                    key=f"delete_{index}"
                ):

                    st.session_state.assignments.remove(item)
                    st.rerun()

st.divider()

# -----------------------------
# SMART STUDY PLAN
# -----------------------------
st.header("🧠 Smart Study Plan")

if not st.session_state.assignments:

    st.info(
        "Add assignments to generate your study plan."
    )

else:

    study_plan = []

    for item in st.session_state.assignments:

        days_left = (
            item["Due Date"] - date.today()
        ).days

        if days_left < 0:
            continue

        # Include today and deadline day
        available_days = days_left + 1

        hours_per_day = (
            item["Estimated Hours"] / available_days
        )

        current_day = date.today()

        for day_number in range(available_days):

            study_date = (
                current_day +
                timedelta(days=day_number)
            )

            study_plan.append(
                {
                    "Date": study_date,
                    "Course": item["Course"],
                    "Task": item["Assignment"],
                    "Study Hours": round(hours_per_day, 1),
                    "Priority": item["Priority"]
                }
            )

    if study_plan:

        plan_df = pd.DataFrame(study_plan)

        plan_df = plan_df.sort_values(
            by=["Date", "Priority"],
            ascending=[True, False]
        )

        st.dataframe(
            plan_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "There are no upcoming assignments to schedule."
        )

st.divider()

# -----------------------------
# WEEKLY VIEW
# -----------------------------
st.header("🗓️ Next 7 Days")

if st.session_state.assignments and study_plan:

    today = date.today()
    next_week = today + timedelta(days=6)

    weekly_plan = plan_df[
        (plan_df["Date"] >= today) &
        (plan_df["Date"] <= next_week)
    ]

    if weekly_plan.empty:

        st.info(
            "No study tasks scheduled for the next 7 days."
        )

    else:

        for current_date in sorted(
            weekly_plan["Date"].unique()
        ):

            st.subheader(
                current_date.strftime("%A, %B %d")
            )

            daily_tasks = weekly_plan[
                weekly_plan["Date"] == current_date
            ]

            for _, task in daily_tasks.iterrows():

                st.write(
                    f'• **{task["Course"]}** — '
                    f'{task["Task"]}: '
                    f'{task["Study Hours"]} hours'
                )

else:

    st.info(
        "Your weekly schedule will appear here."
    )

st.divider()

# -----------------------------
# EXPORT
# -----------------------------
st.header("📥 Export")

if st.session_state.assignments:

    export_data = []

    for item in st.session_state.assignments:

        export_data.append(
            {
                "Course": item["Course"],
                "Assignment": item["Assignment"],
                "Due Date": item["Due Date"],
                "Estimated Hours": item["Estimated Hours"],
                "Priority": item["Priority"]
            }
        )

    export_df = pd.DataFrame(export_data)

    csv = export_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Assignments as CSV",
        data=csv,
        file_name="semester_assignments.csv",
        mime="text/csv"
    )

else:

    st.write(
        "Add assignments before exporting your data."
    )

st.caption(
    "SemesterAI — A student-centered semester planning prototype."
)
