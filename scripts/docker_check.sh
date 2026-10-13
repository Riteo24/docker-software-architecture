#!/bin/bash
set -euo pipefail
task="${1:?Use monolith, hexagonal, microservices or event-driven}"
case "$task" in monolith|hexagonal|microservices|event-driven) ;; *) exit 2 ;; esac
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root/$task"
cleanup() {
    result=$?
    if [ "$result" -ne 0 ]; then
        docker compose logs --no-color
    fi
    # Preserve named volumes; this script also works on a student's workstation.
    docker compose down
    exit "$result"
}
trap cleanup EXIT
docker compose config --quiet
if [ "$task" = microservices ]; then
    for service in catalog users orders; do
        docker build --target test -t "architecture-${service}-tests" "services/$service"
        docker run --rm "architecture-${service}-tests"
    done
else
    docker build --target test -t "architecture-${task}-tests" .
    docker run --rm "architecture-${task}-tests"
fi
docker compose up --build -d --wait --wait-timeout 600
case "$task" in
    monolith)
        docker compose exec -T api python tests/smoke.py
        # Verify that data is preserved after restarting the API.
        docker compose restart api
        docker compose up -d --wait --wait-timeout 120
        docker compose exec -T api python tests/smoke.py
        # Optional Redis implementation and cache invalidation smoke.
        docker compose -f docker-compose.yml -f docker-compose.cache.yml up -d --wait --wait-timeout 120
        docker compose exec -T api python tests/smoke.py
        docker compose -f docker-compose.yml -f docker-compose.cache.yml down
        ;;
    hexagonal)
        docker compose exec -T api python tests/smoke.py
        REPO_ADAPTER=file docker compose up -d --force-recreate --wait --wait-timeout 120 api
        docker compose exec -T api python tests/smoke.py
        # Verify a new repository instance reads the data stored in the CSV volume.
        docker compose exec -T api python -c 'import csv; from config.wiring import repository; rows=list(csv.DictReader(open("/data/orders.csv"))); assert rows; assert repository.get_by_id(rows[-1]["id"]) is not None'
        REPO_ADAPTER=file docker compose restart api
        REPO_ADAPTER=file docker compose up -d --wait --wait-timeout 120 api
        docker compose exec -T api python tests/smoke.py
        REPO_ADAPTER=db docker compose up -d --force-recreate --wait --wait-timeout 120 api
        docker compose exec -T api python tests/smoke.py
        ;;
    microservices)
        docker compose exec -T gateway nginx -t
        # Only the gateway is reachable from the host.
        python3 tests/smoke.py
        ;;
    event-driven)
        docker compose exec -T orders python -m tests.smoke
        docker compose logs --no-color billing notifications
        ;;
esac
echo "PASS: $task Docker unit and smoke tests"
