from main import celery
from utils import openai, NOCODB_TOKEN
from prompts import SUMMARIZE_FINDING
import requests

@celery.task(name='SummarizeFinding', bind=True)
def summarize_finding(self, finding_obj: dict):

    text = f"""Finding {finding_obj.get('key')}"""
    kv = list(finding_obj.items())[2:]
    for k,v in kv:
        if isinstance(v, str):
            text += f"\n{k.capitalize()}: {v}"
        elif k == 'updates':
            text += "Updates:\n"
            for u in v:
                text += f"{u['author']} wrote on {u['date']}:\n{u['body']}\nAttachments: {len(u['attachments'])}"
        elif k == 'risk' and v:
            text += f"Associated risk: {v['description']} (level: {v['level']})"
        elif isinstance(v, list):
            text += f"\n{k.capitalize()}: {', '.join(v)}"


    response = openai.chat.completions.create(
        messages=[
            {'role': 'system', 'content': SUMMARIZE_FINDING},
            {'role': 'user', 'content': text},
        ],
        model="gpt-4o",
        temperature=0.1
    )

    result = response.choices[0].message.content.strip()

    # Update finding summary
    pr = requests.patch("https://aeonow-nocodb-f7wkb.ondigitalocean.app/api/v1/db/data/bulk/noco/AEO Now/Findings", json=[{'Id': finding_obj['id'], 'Summary': result}],
        headers={
            'xc-token': NOCODB_TOKEN
        }).json()
    print(pr)

    return {
        'text': text,
        'summarized': result
    }
