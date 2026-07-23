from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class AIHandler:
    def __init__(self):
        # استفاده از کلاس جدید OpenAI در نسخه های جدید
        self.client = OpenAI(api_key=os.getenv("AI_API_KEY"))

    def get_response(self, prompt, lang):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # یا gpt-4o
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant. Always respond in {lang} language."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Error: {str(e)}"