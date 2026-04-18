# from google import genai
# import json
# import os
# from django.conf import settings

# # genai.configure(api_key=settings.GOOGLE_API_KEY)

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# def generate_summary(text):
#     prompt = f"""
#     Summarize the following content in 4-5 short bullet points.

#     Rules:
#     - Do NOT add any introduction
#     - Do NOT write phrases like "Here is the summary"
#     - Keep it short and direct
#     - Use simple student-friendly language

#     Content:
#     {text}
#     """

#     response = client.models.generate_content(
#         model="gemini-2.0-flash-lite",
#         contents=prompt
#     )
#     # return response.text.strip()
#     return clean_ai_output(response.text)


# def generate_questions(text):
#     prompt = f"""
#     Generate 5 MCQ questions from the following content.

#     Each question must have:
#     - question
#     - 4 options
#     - correct_answer
#     - explanation

#     Return ONLY JSON format like:

#     [
#       {{
#         "question": "...",
#         "options": ["A", "B", "C", "D"],
#         "correct_answer": "A",
#         "explanation": "..."
#       }}
#     ]

#     Content:
#     {text}
#     """

#     response = client.models.generate_content(
#         model="gemini-2.0-flash-lite",
#         contents=prompt
#     )
#     # print("AI RAW RESPONSE:", response.text) x

#     try:
#         return json.loads(response.text)
#     except:
#         return []


# def generate_feedback(question, selected_answer, correct_answer, explanation):
#     prompt = f"""
#     A student answered a question incorrectly.

#     Question: {question}
#     Student Answer: {selected_answer}
#     Correct Answer: {correct_answer}

#     Explanation: {explanation}

#     Give short feedback so that student learn this concept and improve:
#     - Max 2 lines
#     - No introduction
#     - Directly explain what student misunderstood
#     - Suggest what to revise

#     Output should be concise and professional.
#     """

#     response = client.models.generate_content(
#         model="gemini-2.0-flash-lite",
#         contents=prompt
#     )
#     # return response.text.strip()
#     # return response.text.strip()
#     return clean_ai_output(response.text)

# def clean_ai_output(text):
#     unwanted_phrases = [
#         "Here is",
#         "Here are",
#         "To give",
#         "Based on",
#         "I have analyzed",
#         "Below is"
#     ]

#     for phrase in unwanted_phrases:
#         if text.startswith(phrase):
#             text = text.split("\n", 1)[-1]

#     return text.strip()

# def ai_tutor_response(question):
#     prompt = f"""
#     You are an AI tutor helping a student.

#     Answer the question clearly and simply.

#     Rules:
#     - Keep answer short (4-5 lines)
#     - No introduction like "Sure" or "Here is"
#     - Be direct and educational
#     - Use simple language

#     Question:
#     {question}
#     """

#     response = client.models.generate_content(
#         model="gemini-2.0-flash-lite",
#         contents=prompt
#     )
#     return clean_ai_output(response.text)




import json
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- GROQ FIRST ----------
from groq import Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------- GEMINI FALLBACK ----------
try:
    from google import genai
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except:
    gemini_client = None


# ---------- COMMON FUNCTION ----------
def generate_ai_response(prompt):
    # 🔥 TRY GROQ FIRST
    try:
        print("Calling GROQ...")
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": prompt}
            ]
        )
        print("Calling GROQ...")
        return response.choices[0].message.content

    except Exception as e:
        print("Groq failed, switching to Gemini:", e)

    # 🔁 FALLBACK TO GEMINI
    if gemini_client:
        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print("Gemini also failed:", e)

    return "⚠️ AI service is currently unavailable. Please try again."


# ---------- CLEAN OUTPUT ----------
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


# ---------- SUMMARY ----------
def generate_summary(text):
    prompt = f"""
    Summarize the following content in bullet points or if content is large then make summary according to you but cover all the topic

    Rules:
    - Do NOT add any introduction
    - Do NOT write phrases like "Here is the summary"
    - Keep it short and direct
    - Use simple student-friendly language
    Format the summary properly:
    - Use clean bullet points (no symbols like • or - together)
    - Use proper headings
    - Do NOT use symbols like "• -"
    - Keep it structured and readable
    Format the output strictly as:
    - Use headings with **Title**
    - Use only "-" for bullet points
    - Do NOT use "•" or "*"
    - Keep spacing between sections
    NOTE : Always cover full content to summarize means all the content should be in summary
    Content:
    {text}
    """

    response = generate_ai_response(prompt)
    return clean_ai_output(response)


# ---------- QUESTIONS ----------
def generate_questions(text):
    import json

    prompt = f"""
Generate 5 multiple choice questions from the text below.

Return ONLY JSON:

[
  {{
    "question": "Question text",
    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
    "correct_answer": "A",
    "explanation": "short explanation"
  }}
]

TEXT:
{text}
"""

    response = ai_tutor_response(prompt)

    print("RAW AI RESPONSE:", response)

    # ✅ CLEAN MARKDOWN
    response = response.replace("```json", "").replace("```", "").strip()

    try:
        questions = json.loads(response)
    except:
        print("❌ JSON parsing failed")
        questions = []

    return questions


# ---------- FEEDBACK ----------
def generate_feedback(question, selected_answer, correct_answer, explanation):
    prompt = f"""
    A student answered a question incorrectly.

    Question: {question}
    Student Answer: {selected_answer}
    Correct Answer: {correct_answer}

    Explanation: {explanation}

    Give short feedback so that student learn this concept and improve:
    - Max 2-3 lines
    - No introduction
    - Directly explain what student misunderstood
    - Suggest what to revise

    Output should be concise and professional.
    """

    response = generate_ai_response(prompt)
    return clean_ai_output(response)


# ---------- AI TUTOR ----------
def ai_tutor_response(question):
    prompt = f"""
    You are an AI tutor helping a student.

    Answer the question clearly and simply.

    Rules:
    - Keep answer short but can answer long if needed to cover the topic
    - No introduction like "Sure" or "Here is"
    - Be direct and educational
    - Use simple language
    Format your answer properly:
    - Use bullet points
    - Use numbering
    - Add spacing between sections
    - Keep it clean and readable

    Question:
    {question}
    """

    response = generate_ai_response(prompt)
    return clean_ai_output(response)