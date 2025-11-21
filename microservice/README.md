# Grade Microservice Workload

This project processes a grade table, calculates per-student totals and maximum score differences, and demonstrates both monolithic and microservice deployments with Docker.

## Dataset
The grade table lives in `data/Grade Table.csv`. Each row represents a student and their scores for quizzes, assignments, and the final exam.

## Running locally
- **Monolithic app**: `python mono/monolithic.py` (listens on port 8000).
- **Microservices**: `./micro/start_microservices.sh` will start the data, analytics, and API gateway services in tmux panes on ports 5001, 5002, and 5000 respectively.

## Docker
Build and run all containers together:

```sh
docker-compose up --build
```

Services will be available on the same ports exposed above. The API gateway proxies `/grades`, `/metrics`, and `/metrics/summary` to the underlying services.
