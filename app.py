import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="SemesterAI",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "assignments" not in st.session_state:
    st.session_state.assignments = []

if "daily_hours" not in st.session_state:
    st.session_state.daily_hours = {
        "Monday": 2.0,
        "Tuesday": 2.0,
        "Wednesday": 2.0,
        "Thursday": 2.0,
        "Friday": 2.0,
        "Saturday": 3.0,
        "Sunday": 3.0
    }


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def days_remaining(due_date):
    return (due_date - date.today()).days


def priority_score(priority):
    scores = {
        "High": 3,
        "Medium": 2,
        "Low": 1
    }
    return scores.get(priority, 1)


def build_study_plan():
    """
    Create a study plan for incomplete assignments.
    The plan uses:
    - due date
    - priority
    - estimated hours
    - available study hours
    """

    incomplete = [
        a for a in st.session_state.assignments
        if not a["completed"]
    ]

    if not incomplete:
        return pd.DataFrame()

    # Sort by deadline first, then priority.
    incomplete = sorted(
        incomplete,
        key=lambda x: (
            x["due_date"],
            -priority_score(x["priority"])
        )
    )

    remaining_hours = {
        a["id"]: float(a["estimated_hours"])
        for a in incomplete
    }

    plan_rows = []

    today = date.today()

    # Plan up to 30 days ahead.
    for day_offset in range(31):

        current_day = today + timedelta(days=day_offset)
        weekday = current_day.strftime("%A")

        available_hours = float(
            st.session_state.daily_hours.get(weekday, 0)
        )

        if available_hours <= 0:
            continue

        eligible = [
            a for a in incomplete
            if remaining_hours[a["id"]] > 0
            and current_day <= a["due_date"]
        ]

        eligible = sorted(
            eligible,
            key=lambda x: (
                x["due_date"],
                -priority_score(x["priority"])
            )
        )

        for assignment in eligible:

            if available_hours <= 0:
                break

            assignment_remaining = remaining_hours[
                assignment["id"]
            ]

            study_time = min(
                assignment_remaining,
                available_hours
            )

            if study_time <= 0:
                continue

            plan_rows.append({
                "Date": current_day,
                "Course": assignment["course"],
                "Task": assignment["assignment"],
                "Study Hours": round(study_time, 1),
                "Priority": assignment["priority"]
            })

            remaining_hours[assignment["id"]] -= study_time
            available_hours -= study_time

    return pd.DataFrame(plan_rows)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("SemesterAI 🎓")

st.write(
    "Your intelligent semester planning assistant."
)

st.divider()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.header("📊 Dashboard")

total_assignments = len(st.session_state.assignments)

completed_assignments = sum(
    1
    for a in st.session_state.assignments
    if a["completed"]
)

total_hours = sum(
    float(a["estimated_hours"])
    for a in st.session_state.assignments
)

incomplete_assignments = [
    a for a in st.session_state.assignments
    if not a["completed"]
]

if incomplete_assignments:

    next_assignment = min(
        incomplete_assignments,
        key=lambda x: x["due_date"]
    )

    next_deadline = (
        f'{next_assignment["course"]} - '
        f'{next_assignment["assignment"]}'
    )

else:
    next_deadline = "No assignments yet"


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Assignments",
        total_assignments
    )

with col2:
    st.metric(
        "Completed",
        completed_assignments
    )

with col3:
    st.metric(
        "Total Study Hours",
        round(total_hours, 1)
    )

with col4:
    st.metric(
        "Next Deadline",
        next_deadline
    )


# Progress

if total_assignments > 0:

    progress = completed_assignments / total_assignments

    st.write("### Semester Progress")

    st.progress(progress)

    st.caption(
        f"{completed_assignments} of "
        f"{total_assignments} assignments completed "
        f"({progress * 100:.0f}%)"
    )

st.divider()


# --------------------------------------------------
# ADD ASSIGNMENT
# --------------------------------------------------

st.header("➕ Add an Assignment")

with st.form("assignment_form", clear_on_submit=True):

    course = st.text_input(
        "Course Name",
        placeholder="Example: MAT 22A"
    )

    assignment_name = st.text_input(
        "Assignment Name",
        placeholder="Example: Homework 3"
    )

    due_date = st.date_input(
        "Due Date",
        min_value=date.today()
    )

    estimated_hours = st.number_input(
        "Estimated Hours",
        min_value=0.5,
        max_value=100.0,
        value=2.0,
        step=0.5
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

        elif not assignment_name.strip():
            st.error("Please enter an assignment name.")

        else:

            new_assignment = {
                "id": (
                    max(
                        [
                            a["id"]
                            for a
                            in st.session_state.assignments
                        ],
                        default=0
                    )
                    + 1
                ),
                "course": course.strip(),
                "assignment": assignment_name.strip(),
                "due_date": due_date,
                "estimated_hours": float(
                    estimated_hours
                ),
                "priority": priority,
                "completed": False
            }

            st.session_state.assignments.append(
                new_assignment
            )

            st.success("Assignment added!")

            st.rerun()


st.divider()


# --------------------------------------------------
# MY ASSIGNMENTS
# --------------------------------------------------

st.header("📚 My Assignments")

if not st.session_state.assignments:

    st.info(
        "No assignments yet. "
        "Add your first assignment above."
    )

else:

    assignments_sorted = sorted(
        st.session_state.assignments,
        key=lambda x: (
            x["completed"],
            x["due_date"]
        )
    )

    for assignment in assignments_sorted:

        with st.container(border=True):

            title_col, button_col = st.columns(
                [5, 1]
            )

            with title_col:

                if assignment["completed"]:

                    st.subheader(
                        "✅ "
                        + assignment["course"]
                        + " — "
                        + assignment["assignment"]
                    )

                else:

                    st.subheader(
                        assignment["course"]
                        + " — "
                        + assignment["assignment"]
                    )

            with button_col:

                if assignment["completed"]:

                    if st.button(
                        "Undo",
                        key=f'undo_{assignment["id"]}',
                        use_container_width=True
                    ):

                        assignment["completed"] = False
                        st.rerun()

                else:

                    if st.button(
                        "Complete",
                        key=f'complete_{assignment["id"]}',
                        use_container_width=True
                    ):

                        assignment["completed"] = True
                        st.rerun()

            st.write(
                "📅 Due:",
                assignment["due_date"].strftime(
                    "%B %d, %Y"
                )
            )

            st.write(
                "⏱ Estimated time:",
                f'{assignment["estimated_hours"]} hours'
            )

            st.write(
                "🚩 Priority:",
                assignment["priority"]
            )

            remaining = days_remaining(
                assignment["due_date"]
            )

            if assignment["completed"]:

                st.success("Completed!")

            elif remaining < 0:

                st.error(
                    f"Overdue by {abs(remaining)} day(s)"
                )

            elif remaining == 0:

                st.warning("Due today!")

            elif remaining == 1:

                st.warning("Due tomorrow!")

            else:

                st.info(
                    f"{remaining} days remaining"
                )

            if st.button(
                "Delete Assignment",
                key=f'delete_{assignment["id"]}'
            ):

                st.session_state.assignments = [
                    a
                    for a in st.session_state.assignments
                    if a["id"] != assignment["id"]
                ]

                st.rerun()


st.divider()


# --------------------------------------------------
# AVAILABLE STUDY TIME
# --------------------------------------------------

st.header("⏰ My Available Study Time")

st.write(
    "Set how many hours you can study on each day."
)

day_columns = st.columns(7)

days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

for index, day_name in enumerate(days):

    with day_columns[index]:

        st.session_state.daily_hours[day_name] = (
            st.number_input(
                day_name[:3],
                min_value=0.0,
                max_value=12.0,
                value=float(
                    st.session_state.daily_hours[
                        day_name
                    ]
                ),
                step=0.5,
                key=f"hours_{day_name}"
            )
        )


weekly_available = sum(
    st.session_state.daily_hours.values()
)

st.caption(
    f"Total available study time: "
    f"{weekly_available:.1f} hours per week"
)


st.divider()


# --------------------------------------------------
# SMART STUDY PLAN
# --------------------------------------------------

st.header("🧠 Smart Study Plan")

study_plan = build_study_plan()

if not incomplete_assignments:

    st.success(
        "You have no incomplete assignments. Great job!"
    )

elif study_plan.empty:

    st.warning(
        "SemesterAI could not create a study plan. "
        "Try increasing your available study hours."
    )

else:

    display_plan = study_plan.copy()

    display_plan["Date"] = display_plan[
        "Date"
    ].apply(
        lambda x: x.strftime("%Y-%m-%d")
    )

    st.dataframe(
        display_plan,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# --------------------------------------------------
# NEXT 7 DAYS
# --------------------------------------------------

st.header("🗓️ Next 7 Days")

if study_plan.empty:

    st.info(
        "Your weekly study schedule will appear here."
    )

else:

    today = date.today()

    next_week = today + timedelta(days=6)

    weekly_plan = study_plan[
        (study_plan["Date"] >= today)
        &
        (study_plan["Date"] <= next_week)
    ]

    if weekly_plan.empty:

        st.info(
            "No study sessions scheduled "
            "for the next 7 days."
        )

    else:

        for current_day in (
            today + timedelta(days=i)
            for i in range(7)
        ):

            day_plan = weekly_plan[
                weekly_plan["Date"]
                == current_day
            ]

            st.subheader(
                current_day.strftime(
                    "%A, %B %d"
                )
            )

            if day_plan.empty:

                st.caption("No study session.")

            else:

                for _, row in day_plan.iterrows():

                    st.write(
                        f'• **{row["Course"]}** — '
                        f'{row["Task"]}: '
                        f'{row["Study Hours"]} hours'
                    )


st.divider()


# --------------------------------------------------
# EXPORT
# --------------------------------------------------

st.header("📥 Export")

if st.session_state.assignments:

    export_data = []

    for assignment in st.session_state.assignments:

        export_data.append({
            "Course": assignment["course"],
            "Assignment": assignment["assignment"],
            "Due Date": assignment[
                "due_date"
            ].strftime("%Y-%m-%d"),
            "Estimated Hours": assignment[
                "estimated_hours"
            ],
            "Priority": assignment["priority"],
            "Completed": (
                "Yes"
                if assignment["completed"]
                else "No"
            )
        })

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

    if not study_plan.empty:

        plan_export = study_plan.copy()

        plan_export["Date"] = plan_export[
            "Date"
        ].apply(
            lambda x: x.strftime("%Y-%m-%d")
        )

        plan_csv = plan_export.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Study Plan as CSV",
            data=plan_csv,
            file_name="semester_study_plan.csv",
            mime="text/csv"
        )

else:

    st.write(
        "Add assignments before exporting your data."
    )


st.caption(
    "SemesterAI V2 — Smart semester planning "
    "for college students."
)