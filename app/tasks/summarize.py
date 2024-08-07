from main import celery
from utils import openai
from prompts import SUMMARIZE_DEFAULT
import os

@celery.task(name='SummarizeText', bind=True)
def summarize_text(self, text: str):
    response = openai.chat.completions.create(
        messages=[
            {'role': 'system', 'content': SUMMARIZE_DEFAULT},
            {'role': 'user', 'content': text},
        ],
        model=os.environ["AZURE_CHAT_COMPLETIONS_DEPLOYMENT_NAME"],
        temperature=0.1
    )

    result = response.choices[0].message.content.strip()

    return {
        'text': text,
        'summarized': result
    }
