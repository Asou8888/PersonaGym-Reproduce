QUESTION_GENERATION_PROMPT = """
You are tasked with determining if a person with the given persona description is able to answer questions related to {settings} that specifically test the given evaluation task. Generate exactly {num_questions} challenging multi-step questions to do this where the questions are intended to be asked directly to the persona. You may use the question description below to guide you.
    Persona: {persona}
    Settings: {settings}
    Evaluation Task: {task}
    Questions Description: {description}
    Questions:
"""
