# Cloud Computing Project Report

## 1. Background (Yaqi)
Containerized microservices allow independent scaling and easier fault isolation. By separating responsibilities into multiple services, this project mirrors how production systems ensure resilience and maintainability.

## 2. Service Descriptions (Yaqi)
- **Monolithic service**: A single Flask app (`mono/monolithic.py`) that loads the grade table, computes each student's total score and maximum score difference, and exposes `/grades`, `/metrics`, and `/metrics/summary` endpoints.
- **Data service**: Provides the raw grade table via `/grades` and `/grades/<student>`.
- **Analytics service**: Fetches data from the data service and computes totals and maximum score differences for each student. It also summarizes the dataset.
- **API Gateway**: Routes external traffic to the data and analytics services and exposes consolidated `/metrics` and `/metrics/summary` endpoints.

## 3. Containerization Steps (Ziyu + Jiajun)
1. Added `requirements.txt` for shared Python dependencies.
2. Created Dockerfiles for the monolithic app and each microservice (`Dockerfile.monolithic`, `Dockerfile.data_service`, `Dockerfile.analytics_service`, `Dockerfile.api_gateway`).
3. Added `docker-compose.yml` to orchestrate four containers on a shared network with exposed ports (5000-5002 for microservices and 8000 for the monolith).
4. Included the grade dataset in `data/grades.csv` so containers have local access to the input table.

## 4. Results and Analysis (Ziyu + Jiajun)
- **Per-student metrics**: The analytics service returns each student's total score and maximum score difference. The summary endpoint aggregates averages, minimums, and maximums for both metrics.
- **Isolation**: Running `docker-compose up --build` starts isolated containers for the data, analytics, API gateway, and monolithic service, demonstrating both single-container and multi-container deployments.

## 5. Challenges and Resolutions (Ziyu + Jiajun)
- **Data sharing**: Ensuring each container had access to the grade table was solved by copying `data/grades.csv` into every image build context.
- **Service coordination**: Environment variables (`DATA_SERVICE_URL`, `ANALYTICS_SERVICE_URL`) were used so the analytics and gateway services can locate dependencies regardless of runtime hostnames.

## 6. Member Contribution Statement (Yaqi)
- Yaqi: Researched background and described service responsibilities.
- Ziyu: Implemented containerization steps and automation scripts.
- Jiajun: Developed analytics logic and microservice wiring.
