from celery import shared_task
import os
from openai import AzureOpenAI
import numpy as np
import langwatch
from langwatch.types import RAGChunk
import requests
from base64 import b64encode

openai = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"].strip("/"), 
    api_version=os.environ["AZURE_CHAT_COMPLETIONS_VERSION"],  
    api_key=os.environ["AZURE_OPENAI_KEY"],
    max_retries=5
)

def split_into_chunks(s, n):
    lines = s.splitlines()
    chunks = []
    current_chunk = ""
    for line in lines:
        if len(current_chunk) + len(line) + 1 > n:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

@shared_task
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(request.id, exc, traceback))
    return {'error': 'Task {0} raised exception: {1!r}\n{2!r}'.format(request.id, exc, traceback)}


def query_embedding(query: str):
    response = openai.embeddings.create(input=query, model=os.environ["AZURE_TEXT_EMBEDDING_NAME"])
    return response.data[0].embedding

def generate_answer(prompt, multiple_choice=False):
    #langwatch.get_current_trace().autotrack_openai_calls(openai)

    response = openai.chat.completions.create(
        messages=[
            {'role': 'user', 'content': prompt.strip()}
        ],
        model=os.environ["AZURE_CHAT_COMPLETIONS_DEPLOYMENT_NAME"],
        temperature=0.1,
        logprobs=True
    )
    
    logprobs = response.choices[0].logprobs.content
    if multiple_choice:
        logprobs = logprobs[:4] # Limit to the selected option only (first couple of tokens)
    return response.choices[0].message.content, np.round(np.mean([np.exp(lp.logprob)*100 for lp in logprobs]), 2)