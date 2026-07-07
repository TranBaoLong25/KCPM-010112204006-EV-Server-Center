Basic deploy instructions for booking-service

This folder contains a minimal deploy script `deploy.sh` and a sample `docker-compose.yml` you can use on the server.

Steps (minimal):

1. Place files on the server
- Copy `deploy.sh` to `/opt/booking/deploy.sh` and make executable:

```bash
scp deploy/deploy.sh deploy@YOUR_SERVER:/opt/booking/deploy.sh
ssh deploy@YOUR_SERVER 'sudo mkdir -p /opt/booking && sudo chown deploy:deploy /opt/booking || true'
ssh deploy@YOUR_SERVER 'chmod +x /opt/booking/deploy.sh'
```

2. Create a `docker-compose.yml` on server (example below)
- Copy the example file `docker-compose.yml.example` to `/opt/booking/docker-compose.yml` and edit if needed.

```bash
scp deploy/docker-compose.yml.example deploy@YOUR_SERVER:/opt/booking/docker-compose.yml
```

3. Ensure `deploy.sh` is configured correctly
- `deploy.sh` expects environment variables `DOCKERHUB_USERNAME` and `GITHUB_SHA` when executed by the CI. The workflow exports these before calling the script.

4. Test the script manually

```bash
ssh deploy@YOUR_SERVER 'DOCKERHUB_USERNAME=youruser GITHUB_SHA=latest /opt/booking/deploy.sh'
```

5. GitHub Actions
- The repository workflow will call `/opt/booking/deploy.sh` via SSH after building and pushing the image.
- Make sure repository secrets are set: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `SSH_HOST`, `SSH_USER`, `SSH_KEY`.

If the server does not allow writing to `/opt`, use a directory in the deploy user's home (e.g. `/home/deploy/booking`) and update the workflow accordingly.
