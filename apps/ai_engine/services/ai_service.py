from google import genai
import json
import os
from django.conf import settings

# genai.configure(api_key=settings.GOOGLE_API_KEY)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return clean_ai_output(response.text)