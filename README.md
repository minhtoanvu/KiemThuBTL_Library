# 📚 library-qa: Full-Stack Test Automation Portfolio Project

[![CI Pipeline](https://github.com/minhtoanvu/library-qa/actions/workflows/test.yml/badge.svg)](https://github.com/minhtoanvu/library-qa/actions)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-7.x-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A robust, production-grade **Library Management System** bundled with a comprehensive **QA Test Automation Suite**. This project serves as a showcase of modern software testing practices, including Unit Testing, Integration Testing, and End-to-End (E2E) UI Automation using the Page Object Model (POM) design pattern.

---

## 🎯 QA & Testing Highlights

This project was built with a "Quality-First" mindset to demonstrate proficiency in software testing methodologies and test automation frameworks.
### 🔬 Test Automation Capabilities
- **End-to-End (E2E) UI Testing:** Automated critical user journeys (Login, Book Borrowing, Search) using **Selenium WebDriver**.
- **Page Object Model (POM):** Implemented POM for UI tests (`BasePage`, `HomePage`, `LoginPage`, `MyBook`) to ensure high maintainability and code reusability.
- **API & Unit Testing:** Thorough backend testing using **Pytest** for business logic (fines calculation, inventory management, authentication).
- **Test Coverage Analysis:** Integrated **pytest-cov** to measure and report code coverage, ensuring high confidence in code quality.
- **Test Case Design:** Structured manual test cases and scenarios documented in `TESTCASE_LIB.xlsx`.
- **Continuous Integration:** Configured GitHub Actions for automated test execution on every push/pull request.

---

## 🏗️ Technical Stack

### **QA Automation Stack**
- **Framework:** `Pytest` (Test Runner & Assertions)
- **UI Automation:** `Selenium WebDriver`
- **Design Pattern:** Page Object Model (POM)
- **Reporting:** `pytest-cov` (Coverage Reports)
- **CI/CD:** GitHub Actions

### **Application Stack**
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend:** HTML5, CSS3, Jinja2 Templates, Bootstrap
- **Database:** MySQL / SQLite

---

## ⚙️ Project Architecture

```text
library-qa/
├── app/
│   ├── dao/                 # Data Access Objects (Database queries)
│   ├── models/              # SQLAlchemy Database Models
│   ├── templates/           # Jinja2 UI Templates
│   └── tests/               # 🧪 QA Automation Suite
│       ├── BasePage.py      # POM: Base class with common UI actions
│       ├── HomePage.py      # POM: Home page interactions
│       ├── LoginPage.py     # POM: Login page interactions
│       ├── test_*.py        # Pytest Unit & API test files
│       └── test_sel.py      # Selenium E2E test execution
├── index.py                 # Application entry point
├── requirements.txt         # Project dependencies
├── seed_test_data.py        # Database seeding utility for consistent test state
└── TESTCASE_LIB.xlsx        # Comprehensive Test Case specifications
```

---

## 🚀 Getting Started

Follow these steps to set up the environment, run the web application, and execute the test suites.

### 1️⃣ Prerequisites
- Python 3.10 or higher
- Git
- Chrome Browser & ChromeDriver (for Selenium tests)

### 2️⃣ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/minhtoanvu/library-qa.git
cd library-qa

# Create and activate a virtual environment (Recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Seed the database with test data
python seed_test_data.py
```

### 3️⃣ Running the Application

```bash
python index.py
```
The application will be accessible at `http://localhost:5000`.

---

## 🧪 Executing the QA Suite

The test suite is highly modular, allowing you to run specific testing layers.

### Run All Tests
```bash
pytest app/tests/ -v
```

### Run Unit & Integration Tests Only
*(Excludes Selenium UI tests)*
```bash
pytest app/tests/ -v -k "not test_sel"
```

### Run E2E UI Tests (Selenium POM)
```bash
pytest app/tests/test_sel.py -v
```

### Generate Code Coverage Report
```bash
# Display coverage report in terminal
pytest app/tests/ --cov=app --cov-report=term-missing

# Generate an HTML coverage report
pytest app/tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in your browser to view the detailed report
```

---

## 👤 Author

**Minh** 
*QA Automation Engineer / Software Tester*

*If you are reviewing this repository for a QA/Tester role, I highly recommend checking out the `app/tests/` directory to review the Page Object Model implementation and Pytest configurations.*

---

## 📄 License
© 2026 Minh. Licensed under the [MIT License](LICENSE).
