import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-3-flash-preview') 

def generate_summary(text):
    prompt = f"""
    Summarize the following content for a student in simple terms:

    {text}
    """
    response = model.generate_content(prompt)
    return response.text


def generate_questions(text):
    prompt = f"""
    Generate 5 quiz questions from this content:

    {text}
    """
    response = model.generate_content(prompt)
    return response.text


def generate_feedback(text):
    prompt = f"""
    Analyze this content and give improvement feedback:

    {text}
    """
    response = model.generate_content(prompt)
    return response.text