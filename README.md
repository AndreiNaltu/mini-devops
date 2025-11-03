# Mini DevOps — Flask + Docker + Compose (DEV/UAT/PROD) + CI + Healthcheck

[![ci](https://github.com/AndreiNaltu/mini-devops/actions/workflows/ci.yml/badge.svg)](https://github.com/AndreiNaltu/mini-devops/actions)

This project is a small, practical DevOps-style demo: a Python Flask app (with `/` and `/health`), containerized with Docker, run with `docker compose` using DEV / UAT / PROD profiles, tested with `pytest`, and built automatically by GitHub Actions. The pipeline pushes the image to GitHub Container Registry (GHCR).
It also includes a Python health-check script you can run from cron, plus a `RUNBOOK.md` with troubleshooting steps.


## 1. Contents

- `app.py` – Flask app with `/` and `/health`
- `Dockerfile` – container build instructions
- `compose.yml` – run the app with `docker compose` and 3 profiles: `dev`, `uat`, `prod`
- `requirements.txt` – Python dependencies
- `tests/test_health.py` – pytest for the `/health` endpoint
- `tools/health_check.py` – small script to check the service and exit with error if it's down
- `.github/workflows/ci.yml` – GitHub Actions workflow: tests → build → push to GHCR
- `RUNBOOK.md` – operational steps (how to restart, how to check logs, how to rollback)
- `pytest.ini` – makes pytest see the project root on import

Project structure:
```text
.
├── app.py
├── compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
├── RUNBOOK.md
├── requirements.txt
├── tests/
│   └── test_health.py
└── tools/
    └── health_check.py
```


## 2. Run locally (DEV)

You need Docker and the compose plugin.

```bash
docker compose --profile dev up -d
curl -s http://localhost:8080/health   # expected: {"status":"up"}
docker compose --profile dev logs -f
```

Stop:
```bash
docker compose --profile dev down
```

Port 8080 on the host maps to 5000 inside the container.


## 3. Run without Docker (plain Python)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
# in another terminal:
curl -s http://localhost:5000/health
deactivate
```


## 4. Tests (pytest)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
deactivate
```

The test checks that `/health` returns HTTP 200 and JSON `{"status": "up"}`.


## 5. Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

Build & run:
```bash
docker build -t mini-devops:local .
docker run --rm -p 8080:5000 mini-devops:local
```


## 6. `docker compose` with profiles (DEV / UAT / PROD)

`compose.yml`:
```yaml
services:
  web:
    build: .
    image: mini-devops:latest
    ports:
      - "8080:5000"
    environment:
      - FLASK_ENV=production
    profiles: ["dev","uat","prod"]
```

Run with different profiles:
```bash
# DEV
docker compose --profile dev up -d

# UAT
docker compose --profile uat up -d

# PROD
docker compose --profile prod up -d
```


## 7. Health-check script + cron

`tools/health_check.py`:
```python
import sys, requests
URL = "http://localhost:8080/health"
try:
    r = requests.get(URL, timeout=3)
    ok = (r.status_code == 200 and r.json().get("status") == "up")
    sys.exit(0 if ok else 2)
except Exception:
    sys.exit(2)
```

Example cron (every 5 minutes):
```cron
*/5 * * * * /usr/bin/python3 /home/$USER/mini-devops/tools/health_check.py || /usr/bin/logger -t mini-devops "HEALTHCHECK FAILED"
```

If the script exits with a non-zero code, it logs to syslog.


## 8. CI/CD with GitHub Actions

The workflow in `.github/workflows/ci.yml` does:

1. Checkout the repo
2. Set up Python
3. Install dependencies
4. Run pytest
5. Set up Docker Buildx
6. Log in to GHCR using the built-in `GITHUB_TOKEN`
7. Lowercase the repo name (GHCR requires lowercase)
8. Build & push image to `ghcr.io/<github_user>/<repo_name>:latest`

Key part:

```yaml
permissions:
  contents: read
  packages: write
...
      - name: Lowercase repo for GHCR tag
        run: echo "REPO_LC=${GITHUB_REPOSITORY,,}" >> "$GITHUB_ENV"

      - name: Build & push image
        uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ env.REPO_LC }}:latest
```

Every time you `git push` to `main`, GitHub runs tests and publishes a fresh container image.

You can see runs in the **Actions** tab


## 9. Using the image from GHCR

On any machine with Docker:

```bash
docker pull ghcr.io/<GITHUB_USER>/<REPO_NAME>:latest
docker run --rm -p 8080:5000 ghcr.io/<GITHUB_USER>/<REPO_NAME>:latest
```


## 10. RUNBOOK

See `RUNBOOK.md` for typical ops steps, for example:
- check if the container is running
- view logs
- restart the service
- open the firewall port (on Rocky)
- change image tag and re-deploy for rollback



## 11. Troubleshooting

- **\`permission denied: /var/run/docker.sock\`**  
   your user is not in the \`docker\` group or Docker service isn’t running.

- **\`repository name must be lowercase\` in Actions**  
   GHCR needs lowercase tags; this repo already lowercases \`GITHUB_REPOSITORY\`.

- **\`ModuleNotFoundError: app\` when running pytest in Actions**  
   use \`PYTHONPATH=. pytest -q\` or keep \`pytest.ini\` with \`pythonpath = .\`.

- **Actions tab empty**  
   you didn’t push \`.github/workflows/ci.yml\` to \`main\`, or Actions are disabled for this repo.



## 12. Quick commands

```bash
# start dev
docker compose --profile dev up -d

# logs
docker compose --profile dev logs -f

# health
curl -s http://localhost:8080/health

# stop
docker compose --profile dev down
```


## 13. What this project demonstrates

- Linux/docker/compose basic proficiency
- containerizing a Python service
- basic CI with GitHub Actions
- pushing images to a registry (GHCR)
- separating environments (DEV/UAT/PROD) conceptually
- scripting in Python for health checks
- documenting ops with a RUNBOOK
test
