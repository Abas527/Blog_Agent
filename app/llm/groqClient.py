from app.config.settings import Settings
from groq import Groq

client=Groq(
    api_key=Settings.GROQ_API_KEY
)


def generate_response(model,prompt):
    response=client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],temperature=0.7
    )
    return response.choices[0].message.content