# CV-Job Matching System with RAG and Recommendation Engine
An intelligent CV parsing and job recommendation system powered by Large Language Models (LLMs), vector databases, and semantic search.
Documentation Link:
## Get Started on local computer

### Installation

#### Quick Start
1. **Clone the repository**
```bash
git clone git@github.com:creatorof/CV_Job_Matching_Syste.git
cd CV_Job_Matching_Syste
```

2. **Configure environment**
Set the environment variable in .env file
```bash
PGADMIN_EMAIL=pgadmin-email-placeholder
PGADMIN_PASSWORD=pgadmin-password-placeholder

SECRET_KEY = secret-key-placeholder
LLM_API_KEY=llm-api-key-placeholder

POSTGRES_USER=postgres-user-placeholder
POSTGRES_PASSWORD=postgres-password-placeholder
```

3. **Run Docker**
```bash
docker compose up --build
```

4. **Exit the application**
```bash
docker compose down
```



