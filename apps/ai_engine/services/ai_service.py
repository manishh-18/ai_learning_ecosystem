import google.generativeai as genai
import json
from django.conf import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-3-flash-preview') 

def generate_summary(text):
    prompt = f"""
    Summarize the following content in 4-5 short bullet points.

    Rules:
    - Do NOT add any introduction
    - Do NOT write phrases like "Here is the summary"
    - Keep it short and direct
    - Use simple student-friendly language

    Content:
    {text}
    """

    response = model.generate_content(prompt)
    # return response.text.strip()
    return clean_ai_output(response.text)


def generate_questions(text):
    prompt = f"""
    Generate 5 MCQ questions from the following content.

    Each question must have:
    - question
    - 4 options
    - correct_answer
    - explanation

    Return ONLY JSON format like:

    [
      {{
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "..."
      }}
    ]

    Content:
    {text}
    """

    response = model.generate_content(prompt)
    # print("AI RAW RESPONSE:", response.text) x

    try:
        return json.loads(response.text)
    except:
        return []


def generate_feedback(question, selected_answer, correct_answer, explanation):
    prompt = f"""
    A student answered a question incorrectly.

    Question: {question}
    Student Answer: {selected_answer}
    Correct Answer: {correct_answer}

    Explanation: {explanation}

    Give short feedback so that student learn this concept and improve:
    - Max 2 lines
    - No introduction
    - Directly explain what student misunderstood
    - Suggest what to revise

    Output should be concise and professional.
    """

    response = model.generate_content(prompt)
    # return response.text.strip()
    # return response.text.strip()
    return clean_ai_output(response.text)

def clean_ai_output(text):
    unwanted_phrases = [
        "Here is",
        "Here are",
        "To give",
        "Based on",
        "I have analyzed",
        "Below is"
    ]

    for phrase in unwanted_phrases:
        if text.startswith(phrase):
            text = text.split("\n", 1)[-1]

    return text.strip()

def ai_tutor_response(question):
    prompt = f"""
    You are an AI tutor helping a student.

    Answer the question clearly and simply.

    Rules:
    - Keep answer short (4-5 lines)
    - No introduction like "Sure" or "Here is"
    - Be direct and educational
    - Use simple language

    Question:
    {question}
    """

    response = model.generate_content(prompt)
    return clean_ai_output(response.text)