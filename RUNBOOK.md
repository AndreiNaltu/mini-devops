# RUNBOOK — mini-devops (Rocky Linux)

## 1. Site not responding

1. Check if the container is running:
   docker compose --profile dev ps

2. Check the service logs:
   docker compose --profile dev logs web

3. Check the health endpoint locally:
   curl -s http://localhost:8080/health

4. Try a restart of the service:
   docker compose --profile dev restart web

5. Check if the port is listening and if the firewall allows it:
   ss -ltnp | grep 8080
   sudo firewall-cmd --list-ports
   If 8080 is not open:
     sudo firewall-cmd --add-port=8080/tcp --permanent
     sudo firewall-cmd --reload

6. Full redeploy (bring down and up again):
   docker compose --profile dev down
   docker compose --profile dev up -d

## 2. Image rollback (prod)

1. Pick a known-good image tag from GHCR.
2. In compose.yml set:
   image: ghcr.io/<user>/<repo>:<tag>
3. Redeploy with the prod profile:
   docker compose --profile prod up -d --pull always
4. Verify:
   curl -s http://localhost:8080/health

## 3. Post-restart checks

- curl /health returns 200 and JSON { "status": "up" }
- No new HEALTHCHECK FAILED entries in syslog/journal:
  sudo journalctl -f | grep mini-devops
