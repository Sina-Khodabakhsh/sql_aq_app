# SQL Question Answering App

## Overview

This project is a **Streamlit-based web application** that enables users to ask business questions in natural language and automatically converts them into **Microsoft SQL Server queries** using a **Large Language Model (LLM)**.

The application executes the generated SQL query on a database and returns:

- The generated SQL query  
- A clear, human-readable answer based on the query results  

This project demonstrates how LLMs can be integrated with structured data systems to enable **natural language-driven analytics**.

The application is built and tested using the **AdventureWorksDW2019** sample data warehouse.

---

## Demo

### Demo 1
![Demo 1](Demo/Demo01.gif)

### Demo 2
![Demo 2](Demo/Demo02.gif)

---

## Technologies Used

The application is built using the following technologies:

- **Python** — Core programming language  
- **Streamlit** — Interactive web interface  
- **LangChain** — LLM orchestration and chaining  
- **OpenAI API** — Natural language to SQL generation and answer synthesis  
- **SQLAlchemy** — Database connectivity and query execution  
- **PyODBC** — Microsoft SQL Server driver  
- **Pydantic** — Structured output validation  
- **Pandas** — Data processing and result handling  

---

## How to Run the Application

### 1. Clone the repository


git clone https://github.com/Sina-Khodabakhsh/sql_aq_app.git
cd sql_aq_app

---

### 2. Create a virtual environment

Windows  
python -m venv venv  
venv\Scripts\activate  

macOS / Linux  
python3 -m venv venv  
source venv/bin/activate  

---

### 3. Install dependencies

pip install -r requirements.txt  

---

### 4. Set environment variables

Create a `.env` file in the root directory and add:

OPENAI_API_KEY=your_openai_api_key  
LANGCHAIN_API_KEY=your_langchain_api_key  

---

### 5. Configure database connection

from sqlalchemy.engine import URL  

connection_url = URL.create(  
    "mssql+pyodbc",  
    host="YOUR_SERVER_NAME",  
    database="YOUR_DATABASE_NAME",  
    query={  
        "driver": "ODBC Driver 17 for SQL Server",  
        "trusted_connection": "yes",  
    },  
)  

---

### 6. Run the application

streamlit run app.py  

After running, open your browser and navigate to:  
http://localhost:8501  

---

## Usage

1. Enter a business question in the input field  
2. Click the Run button  
3. The application will:  
   - Generate a SQL query  
   - Execute it against the database  
   - Return both the SQL query and a natural language answer  

---

## Notes

- The sample database used in this project is **AdventureWorksDW2019**  
- Only SELECT queries are permitted for safety  
- The model operates strictly within the provided schema  
- Output quality depends on the clarity and specificity of the input question  

---

## Purpose

This project is designed as a portfolio-grade application to demonstrate:

- Integration of LLMs with SQL databases  
- Application of AI in real-world business analytics scenarios  
- How AI can accelerate the data analysis process and data modeling