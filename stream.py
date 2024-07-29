import streamlit as st
import pandas as pd
import random

# Load questions from CSV
csv_file_path = "aws_questions.csv"
questions_df = pd.read_csv(csv_file_path)

# Initialize session state
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answered" not in st.session_state:
    st.session_state.answered = set()
if "score" not in st.session_state:
    st.session_state.score = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = {}
if "show_answers" not in st.session_state:
    st.session_state.show_answers = False

# Function to generate a new set of questions
def generate_questions():
    selected_questions = questions_df.sample(30)
    st.session_state.questions = selected_questions.to_dict("records")
    st.session_state.answered = set()
    st.session_state.user_answers = {}
    st.session_state.correct_answers = {}
    st.session_state.score = 0
    st.session_state.show_answers = False
    for _, row in selected_questions.iterrows():
        correct_answer = (
            row["correct_answer"].strip().replace(" ", "").upper()
        )  # Normalize correct answer
        options = [
            row[f"option{i}"] for i in range(1, 6) if pd.notna(row[f"option{i}"])
        ]
        # Store the correct answer using option values
        if len(correct_answer) > 1:  # Multiple answers
            correct_options = [
                options[ord(c) - 65] for c in correct_answer
            ]  # Convert letters to values
            st.session_state.correct_answers[row["question"]] = correct_options
        else:
            correct_option = options[
                ord(correct_answer) - 65
            ]  # Convert letter to value
            st.session_state.correct_answers[row["question"]] = [correct_option]

# Function to generate result file
def generate_result_file(
    score, total_questions, percentage, user_answers, correct_answers
):
    filename = f"result_{random.randint(1000, 9999)}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Score: {score}/{total_questions}\n")
        f.write(f"Percentage: {percentage}%\n\n")
        f.write("Your Answers:\n")
        for question in st.session_state.questions:
            q_text = question["question"]
            correct_answer = " ".join(correct_answers[q_text])
            user_answer = user_answers.get(q_text, "Not answered")
            f.write(f"Question: {q_text}\n")
            f.write(f"Your Answer: {user_answer}\n")
            f.write(f"Correct Answer: {correct_answer}\n\n")
    return filename

# Generate questions on the first run
if not st.session_state.questions:
    generate_questions()

st.title("Quiz")

# Display the quiz form
with st.form(key="quiz_form"):
    for index, row in enumerate(st.session_state.questions):
        question_number = index + 1
        if row["question"] not in st.session_state.answered:
            st.markdown(f"**{question_number}. {row['question']}**")

            # Extract options from the row
            options = [
                row[f"option{i}"] for i in range(1, 6) if pd.notna(row[f"option{i}"])
            ]
            correct_answer = (
                row["correct_answer"].strip().replace(" ", "").upper()
            )  # Normalize correct answer

            if len(correct_answer) > 1:  # Multiple answers
                correct_options = sorted(
                    [options[ord(c) - 65] for c in correct_answer]
                )  # Convert letters to values
                selected_options = st.multiselect(
                    f"Select the correct options for question {question_number}",
                    options,
                    key=f"multiselect-{index}",
                )
                user_answer = sorted(selected_options)
                st.session_state.user_answers[row["question"]] = user_answer
                st.session_state.answered.add(row["question"])
                if user_answer == correct_options:
                    st.session_state.score += 1
            else:
                # Use radio buttons for single correct answer
                selected_option = st.radio(
                    "Select the correct option", options, key=f"radio-{index}"
                )
                if selected_option:  # Ensure the user changes from the placeholder
                    user_answer = selected_option
                    st.session_state.user_answers[row["question"]] = user_answer
                    st.session_state.answered.add(row["question"])
                    if user_answer == options[ord(correct_answer) - 65]:
                        st.session_state.score += 1

    # Submit button within the form
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        all_answered = len(st.session_state.answered) == len(st.session_state.questions)
        if all_answered:
            percentage = (
                st.session_state.score / len(st.session_state.questions)
            ) * 100
            st.write(f"Your score: {percentage}%")
            result_filename = generate_result_file(
                st.session_state.score,
                len(st.session_state.questions),
                percentage,
                st.session_state.user_answers,
                st.session_state.correct_answers,
            )
            st.write(f"Results saved to {result_filename}")
            st.session_state.show_answers = True
        else:
            st.warning("Please answer all questions before submitting.")

if st.session_state.show_answers:
    st.write("### Correct Answers")
    for index, row in enumerate(st.session_state.questions):
        question_number = index + 1
        st.markdown(f"**{question_number}. {row['question']}**")

        options = [
            row[f"option{i}"] for i in range(1, 6) if pd.notna(row[f"option{i}"])
        ]
        correct_answers = st.session_state.correct_answers[row["question"]]
        user_answer = st.session_state.user_answers.get(row["question"], "Not answered")

        for option in options:
            if option in correct_answers:
                st.markdown(f"<span style='color: green;'>{option}</span>", unsafe_allow_html=True)
            elif option == user_answer:
                st.markdown(f"<span style='color: red;'>{option}</span>", unsafe_allow_html=True)
            else:
                st.write(option)

    st.write("### Your Score")
    st.write(f"Score: {st.session_state.score}")
    st.write(f"Percentage: {percentage}%")
