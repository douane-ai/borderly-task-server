# fruit-task-service

Run command:

```
cd app &
celery -A main.celery worker --pool=gevent --loglevel=info --without-mingle --without-gossip --without-heartbeat &
uvicorn --host 0.0.0.0 --port 8000 main:app
```

Be sure to kill all celery workers when shutting down:

```
pkill -f 'celery worker'
```

## Task decorator params

Use `bind=True` so that the function has access to thr task instance. This allows for updating the state or for retries:

```
@task(bind=True)
def hello(self, a, b):
    time.sleep(1)
    self.update_state(state="PROGRESS", meta={'progress': 50})
    time.sleep(1)
    self.update_state(state="PROGRESS", meta={'progress': 90})
    time.sleep(1)
    return 'hello world: %i' % (a+b)
```

```
@task(bind=True, max_retries=5)
def retrying(self):
    try:
        return 1/0
    except Exception:
        self.retry(countdown=5)
```

## Env vars

```
CELERY_BROKER_URL=amqps://user:pass@host:port
CELERY_RESULT_BACKEND=dynamodb://...:...@eu-central-1:443/celery

# General AzureOpenAI
AZURE_OPENAI_ENDPOINT=https://passionfruit-france-central.openai.azure.com
AZURE_OPENAI_KEY=...

# GPT-4
AZURE_CHAT_COMPLETIONS_DEPLOYMENT_NAME=...
AZURE_CHAT_COMPLETIONS_VERSION=2024-05-01-preview

# ADA-002
AZURE_TEXT_EMBEDDING_NAME=fruit-text-embedding-ada-002

# LangWatch
LANGWATCH_API_KEY=...
```
