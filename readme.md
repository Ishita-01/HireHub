# HireHub

HireHub is a comprehensive, AI-powered career management platform designed to streamline the internship and job search process for students. It integrates automated job scraping, resume analysis, and application tracking into a single, cohesive workflow.

## Key Features

* **Intelligent Job Scraping**: Aggregates opportunities from both external web sources and internal on-campus placement cell communications (via Gmail API & document parsing).
* **AI Resume Analysis**: Leverages Google Gemini to perform deep, objective analysis of resumes against specific job descriptions, providing match scores, skill gap identification, and actionable ATS improvement recommendations.
* **Application Pipeline Management**: A centralized dashboard to track application status, manage notes, and organize career milestones .
* **Role-Based Access Control**: Distinguishes between standard student users and administrative users who can manage the job database.

## Statistical Insights

HireHub optimizes the job hunting process with the following capabilities:

* **Automated Data Processing**: Syncs jobs from multiple platforms and email inboxes, reducing manual search time.
* **AI-Driven Benchmarking**: Provides granular feedback with category-specific scoring (Skills, Experience, Achievements, Keywords, and Qualifications), each weighted by their impact on overall ATS compatibility.
* **Structured Pipeline**: Tracks applications across 7 unique status categories (Planned, Applied, OA, Interview, Offer, Rejected, Ghosted) to maintain a clean overview of career progress.
* **Scalable Architecture**: Built using a containerized approach (Docker) for consistent deployment and performance.

## Tech Stack

* **Backend**: FastAPI, SQLAlchemy, SQLite 
* **AI/LLM**: Google Gemini (`google-genai` library) 
* **Data Processing**: Pandas, Python-Docx 
* **Frontend**: Jinja2 Templates, Bootstrap 5 
* **Deployment**: Docker, Uvicorn 

## Getting Started

### Prerequisites

* Docker and Docker Compose
* A Google Cloud Project with Gmail API and Gemini API enabled
* `credentials.json` for Google API authentication

### Setup

1.  **Clone the repository**.
2.  **Configure environment**: Create a `.env` file and add your `GEMINI_API_KEY`.
3.  **Authentication**: Place your Google API `credentials.json` in `app/core/` and ensure `token.json` is generated upon first run.
4.  **Launch**:
    ```bash
    docker-compose up --build
    ```
5.  **Access**: The application will be running at `http://localhost:8000`.

---
*Built with ❤️ for efficient career management.*
