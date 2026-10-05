# Service containers: native vs. manual

Every infra dependency `docker-compose.test.yml` declares needs an
equivalent in CI. Two shapes, pick per dependency:

## Native service container (preferred — use whenever the provider supports it)

GitHub Actions `services:` (and equivalents in other providers) can pass
image, env, ports, and a healthcheck — enough for any image whose entrypoint
already does the right thing with just environment variables. Postgres is
the common case:

```yaml
jobs:
  <toolchain>:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: <same image:tag as docker-compose.test.yml>
        env:
          POSTGRES_USER: <same fixture user>
          POSTGRES_PASSWORD: <same fixture password>
          POSTGRES_DB: <same fixture db name>
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U <user> -d <db>"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
          --health-start-period 10s
    steps:
      - uses: actions/checkout@<sha> # v7
        with:
          persist-credentials: false
      # ... toolchain setup, then the check steps
```

The app connects to `localhost:5432` (or `127.0.0.1`), not a compose network
hostname — GitHub Actions service containers share the job's network
namespace with the runner, unlike a compose bridge network.

## Object store as a native service (GitHub Actions)

GitHub Actions services accept `command:` and `entrypoint:` (Docker
Compose names and behavior) since April 2026
(github.blog/changelog/2026-04-02-github-actions-early-april-2026-updates),
so an image that needs a non-default command is still a native service.
SeaweedFS (`chrislusf/seaweedfs`) needs none — its default `CMD` is
`mini -dir=/data`, which serves the S3 API on 8333 — but set
`command:` to whatever `docker-compose.test.yml` sets, if anything. Any
S3-compatible image works; verify it pulls.

```yaml
    services:
      <store>:
        image: <same image:tag as docker-compose.test.yml>
        # command: <only if docker-compose.test.yml overrides it>
        env:
          AWS_ACCESS_KEY_ID: <same fixture value as compose>
          AWS_SECRET_ACCESS_KEY: <same fixture value as compose>
        ports:
          - 8333:8333
        options: >-
          --health-cmd "curl -fsS http://127.0.0.1:8333/healthz"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
    steps:
      # ... checkout, toolchain setup
      - name: Create <store> bucket
        run: |
          docker run --rm --network host \
            -e AWS_ACCESS_KEY_ID=<same fixture value> \
            -e AWS_SECRET_ACCESS_KEY=<same fixture value> \
            -e AWS_DEFAULT_REGION=us-east-1 \
            --entrypoint /bin/sh amazon/aws-cli:<pinned-tag> -c \
            'aws --endpoint-url http://127.0.0.1:8333 s3api head-bucket --bucket <bucket> || aws --endpoint-url http://127.0.0.1:8333 s3 mb s3://<bucket>'
```

The job starts steps only after every service's health check passes, so
the bucket step needs no retry loop.

## Manual container + readiness poll (fallback: providers that can't override the image's command)

Use this only on a provider whose service config can set image/env/ports
but not the command `docker-compose.test.yml` uses. Run the image as a
plain step instead of a service container:

```yaml
      - name: Start <object-store>
        run: |
          docker run -d --name ci-<object-store> \
            -p 127.0.0.1:<port>:<port> \
            -e <ACCESS_KEY_VAR>=<same fixture value as compose> \
            -e <SECRET_KEY_VAR>=<same fixture value as compose> \
            <image> <same command docker-compose.test.yml uses>

      - name: Create <object-store> bucket
        run: |
          for i in $(seq 1 30); do
            if docker run --rm --network host --entrypoint /bin/sh <cli-image> -c \
              '<same bucket-create command docker-compose.test.yml's init service uses>'; then
              exit 0
            fi
            sleep 1
          done
          echo "<object-store> bucket setup failed after 30 attempts"
          exit 1
```

The retry loop replaces compose's `depends_on: condition: service_healthy` —
there is no equivalent ordering primitive for a manually-run container, so the
poll is the substitute. Thirty attempts at one second apart is a starting
budget; widen it only if the real image's cold-start time measured in
practice needs more, not preemptively.

## Choosing between them

| The image... | Use |
|---|---|
| Only needs env vars to behave correctly (most databases) | Native service container |
| Needs a non-default command/entrypoint argument | Native with `command:` / `entrypoint:` on GitHub Actions; manual container + poll on a provider without them |
| Has a provider-native readiness/health option | Native, with `options: --health-cmd ...` |
| Has none | Manual container + poll, since there is nothing for `services:` to check |

Whichever shape, the values inside — image tag, credentials, bucket/db name,
command — are copied from `docker-compose.test.yml`, never re-decided here.
