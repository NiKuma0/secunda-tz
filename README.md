# How to run in docker

1. Run it in docker compose:

    ```
    sudo docker compose -f docker-compose.prod.yaml up
    ```

2. Go to http://localhost:8000/docs to see API documentation.

# How to run locally

1. You'll need [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run this command:

    ```
    uv sync
    ```

3. Then this:

    ```
    uv run python main.py
    ```
