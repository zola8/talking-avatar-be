# talking-avatar-be

FastAPI backend for the React Talking Avatar app.

### Install dependencies

You must have **uv**: `pip install uv`

Then:

```shell
uv sync --upgrade
```

### Build locally

```
docker build -t talking-avatar-be .

docker run -p 8080:8080 -e AZURE_SPEECH_REGION=westeurope -e AZURE_SPEECH_KEY=XXX talking-avatar-be
```
