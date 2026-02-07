# Gen-AI---QA-
# 🛡️ Jarvis: Enterprise QA Generation Tool

Jarvis is an AI-powered Software Testing Life Cycle (STLC) orchestrator designed to automate the transition from User Stories to executable Test Automation scripts. Built with Streamlit and OpenAI, it integrates directly with Jira and Azure DevOps to streamline the QA process.

## 🚀 Features

* **User Story AI Evaluator:** Audits requirements against INVEST criteria and flags ambiguities.
* **BDD/Gherkin Preparation:** Automatically converts stories into Given-When-Then scenarios.
* **Multi-Path Test Generation:** Creates Happy, Negative, and Edge case test suites.
* **Edge Case Explorer:** Identifies Security (OWASP), Performance, and Concurrency vulnerabilities.
* **Script Generator:** Produces boilerplate code for Cypress, Playwright, and Selenium.
* **Data Factory:** Generates synthetic, PII-compliant test data using Faker.
* **Execution Feedback Loop:** Analyzes error logs and stack traces to provide Root Cause Analysis (RCA).
* **Sync & Export:** Pulls requirements from Jira/Azure and exports test cases via Jira-compatible CSV.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **AI Engine:** [OpenAI API](https://openai.com/api/) (GPT-4o / GPT-4-Turbo)
- **Data Generation:** [Faker](https://faker.readthedocs.io/)
- **Integrations:** Jira REST API, Azure DevOps REST API

---

## 📦 Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/jarvis-qa-tool.git](https://github.com/your-username/jarvis-qa-tool.git)
   cd jarvis-qa-tool
