# **App**


## Project goals 🎯

This application predicts flight delays before departure and after landing, enabling travellers to anticipate disruptions and reorganize their plans accordingly — whether it's adjusting a pick-up time, rescheduling a connection, or managing last-minute logistics.
By leveraging historical flight data and real-time indicators, it empowers individuals with actionable insights so they can stay one step ahead of airline disruptions.

---


# Installation

## Method 1 : with Docker Desktop

1. Install **Docker Desktop**: From [www.docker.com](https://www.docker.com/products/docker-desktop/)
   Start Docker Desktop.

2. Clone the Git repository to your local machine and move there:

```bash
git clone https://gitlab-mi.univ-reims.fr/touz0012/management_projet_digitaux.git
cd App
```

Launch our app
```
 docker compose -f .devcontainer/docker-compose.yaml up --build app
```

> This command builds the image, installs dependencies via **UV**,
> and automatically runs your main script (`src/App/main.py`).

To stop the app:

```bash
docker compose down
```


## Method 2 : by installing Python and UV manually

1. Install **Python 3.13+**: From [Python.org](https://www.python.org/).

2. Install **UV**: From [https://docs.astral.sh/uv](https://docs.astral.sh/uv).

3. Clone the Git repository to your local machine and move there:

```bash
git clone https://gitlab-mi.univ-reims.fr/touz0012/management_projet_digitaux.git
cd App
```

4. Run our app (caution: first run installs dependencies and can take a while):

```bash
uv sync
uv run streamlit run src/App/main.py

```

---


# The repository is structured as follows : 

- **`.devcontainer/`** 📂
    - Development container configuration
- **`.streamlit/`** 📂
    - Contains configuration files for the Streamlit interface.
- **`data/`** 📂
    - Contains the datasets used for the App project.
        - **`processed/`** 📂 : cleaned and harmonized datasets ready for modeling    
        - **`raw/`** 📂 : Original datasets dowloaded from FRED ans Eurostat APIs
- **`documents/`** 📂
    - Includes documentation related to the project.
        - `App_customer_presentation_sprint_1.pptx` : Presentation slides for the first sprint review
        - `logigramme_App.png` : Diagram illustrating the interface logic
        - `roadmap_App.pdf` : The planning of this project
        - `variable_glossary.pdf` : Glossary describing all variables and their economic meaning
- **`src/`** 📂
    - Contains Python scripts for App project.
        - **`App/`** 📂
            - Main application package
                - **`analysis/`** 📂 : Scripts for exploratory data analysis and visualization
                - **`config/`** 📂 : Centralized configuration: paths, constants, global variables, environment overrides
                - **`data_ingestion/`** 📂 : Scripts for API calls, data extraction and storage
                - **`interface/`** 📂 : Dashboard and visualisation layer for end users
                - **`models/`** 📂 : Machine leaning models and pridiction logic
                - **`preprocessing/`** 📂 : Data cleaning, transformation and feature engineering
        - `__init__.py` : Package initializer
        - `main.py` : Application entrypoint used to launch the App interface
- **`tests/`** 📂 
    - Contains unit tests to ensure code reliability and robustness.
        - **`test_analysis/`** 📂 : Tests for data exploration, visualization, and statistical analysis functions
        - **`test_data_ingestion/`** 📂 : Tests for data collection and API connection
        - **`test_interface/`** 📂 : Tests for user interface components and dashboard rendering 
        - **`test_models/`** 📂 : Tests for model training and evaluation
        - **`test_preprocessing/`** 📂 : Tests for data transformation functions
        - `conftest.py` : Shared pytest configurationand fixtures

- `.gitattributes` : Git configuration for consistent line endings and diffs
- `.gitignore` : Ignore temporary and environment-specific files
- `gitlab-ci.yml` : GitLab CI/CD configuration for automated testing and deployment
- `.pre-commit-config.yaml` : Pre-commit hooks: Ruff linting, formatting, whitespace cleanup, TOML checks
- `README.md` : A document describing the project's organization and usage
- `pyproject.toml` : Project configuration and dependency management (Poetry)
- `uv.lock` : Fully resolved dependency lockfile ensuring reproducible environments

---


# Dataset 📚

## About the database



---


# 🤝 Authors and acknowledgment

The application was developed by students of the Master's program in « Statistique pour l’Évaluation et la Prévision » at the University of Reims Champagne-Ardenne, Class of 2025–2026. Below are the contributors and their respective roles :  
- **BELLO Sadate** (APE) : Data Scientist
- **SEYE Pape Ndiogou** (APE) - alternant : Data Engineer
- **AKODEKOU Crespin** (MA) : Data Analyst
- **PHOLULAMDETH Antoine** (MA) : Front End / User Interface
- **TOUZANI Sofiane** (MA) : Product Owner / Data Governance
