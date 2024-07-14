
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    # 1. Validate the provided answer
    if not isinstance(answer, str) or not answer.strip():
        return False, "Answer must be a non-empty string."

    # 2. Store the answer in the Django session
    if 'answers' not in session:
        session['answers'] = {}
    
    session['answers'][current_question_id] = answer
    session.modified = True  # Mark the session as modified to ensure it gets saved
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    # Find the index of the current question
    current_index = next((index for (index, d) in enumerate(PYTHON_QUESTION_LIST) if d["id"] == current_question_id), None)

    if current_index is None:
        return "Current question ID not found.", -1

    # Calculate the index of the next question
    next_index = current_index + 1

    # Check if next question exists
    if next_index < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_index]
        return next_question["question"], next_question["id"]
    else:
        return "No more questions.", -1

    return "dummy question", -1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    # Retrieve user's answers from the session
    user_answers = session.get('answers', {})

    # Initialize score
    score = 0

    # Calculate the score
    for question in PYTHON_QUESTION_LIST:
        question_id = question["id"]
        correct_answer = question["answer"]
        user_answer = user_answers.get(str(question_id), "")

        # Simple comparison for correct answers
        if user_answer.strip().lower() == correct_answer.strip().lower():
            score += 1

    # Create the final result message
    total_questions = len(PYTHON_QUESTION_LIST)
    result_message = f"You answered {score} out of {total_questions} questions correctly."

    return result_message

    
