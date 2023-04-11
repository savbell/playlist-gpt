from app import openai, os

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

def ask_model(messages):
    response = openai.ChatCompletion.create(
        model=openai_model,
        messages=messages,
    )
    return response.choices[0]["message"]["content"]
