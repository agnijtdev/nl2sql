# NL2SQL — Natural Language to SQL

## Overview

NL2SQL is a Natural Language Interface for Databases (NLIDB) that allows users to query a database using plain English. The system converts natural language questions into SQL queries using a fine-tuned T5 model trained on the Spider dataset and executes them against a connected SQLite database.

### Features

- Natural Language → SQL conversion
- Fine-tuned T5 Transformer model
- Dynamic database schema extraction
- Interactive terminal interface
- Query clarification for ambiguous requests
- SQL validation before execution
- Query history tracking
- CSV export support
- Rich terminal UI
- SQLite database integration

---

# Project Architecture

```text
User Question
      │
      ▼
 Clarifier
      │
      ▼
 Schema Loader ───► Database Schema
      │
      ▼
 NL2SQL Engine (Fine-tuned T5)
      │
      ▼
 Generated SQL
      │
      ▼
 SQL Validator
      │
      ▼
 Database Executor
      │
      ▼
 Results Renderer
```

---

# Directory Structure

```text
nl2sql/
├── colab/
│   └── train_nl2sql.ipynb
│
├── model/
│   └── nl2sql_model/
│
├── app/
│   ├── main.py
│   ├── nl2sql_engine.py
│   ├── schema_loader.py
│   ├── db_executor.py
│   ├── clarifier.py
│   └── renderer.py
│
├── databases/
│   ├── sample.db
│   └── create_sample_db.py
│
├── requirements.txt
└── README.md
```

---

## Software

- Python 3.10+
- SQLite
- Google Colab (recommended for training)

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd nl2sql
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

# Install Dependencies

pip install -r requirements.txt


Verify:
python -c "import transformers, torch; print('Setup OK')"


---

# Dataset

This project uses the Spider Dataset.

Dataset Characteristics:

- 7,000+ training examples
- 1,000+ validation examples
- 200 databases
- Complex multi-table SQL queries


# Model Training

## Training Environment

Recommended:
- Google Colab GPU (T4)
---

## Install Training Dependencies

```python
!pip install transformers datasets sentencepiece torch accelerate -q
```

---

## Model Selection

### Option 1: Train From Scratch

```python
MODEL_NAME = "t5-base"
```

### Option 2: Faster Alternative

```python
MODEL_NAME = "t5-small"
```

### Option 3: Best Performance

```python
MODEL_NAME = "gaussalgo/T5-LM-Large-text2sql-spider"
```

---

## Start Training

```python
trainer.train()
```

Approximate training time:

| GPU | Time |
|------|------|
| T4 | 1.5–2 Hours |
| A100 | 20–30 Minutes |

---

## Save Model

```python
model.save_pretrained("./nl2sql_model")
tokenizer.save_pretrained("./nl2sql_model")
```

---

## Download Model

```python
!zip -r nl2sql_model.zip ./nl2sql_model
```

Place the extracted folder inside:

```text
model/nl2sql_model/
```

---

# Creating Test Database

Run:

```bash
python databases/create_sample_db.py
```

This creates:

```text
databases/sample.db
```

Tables:

- customers
- products
- orders

---

# Running the Application

## Launch

```bash
python app/main.py --db databases/sample.db --model model/nl2sql_model
```

# Sample Queries

```text
show all customers

find the most expensive product

how many orders were placed last month

list pending orders

which city has the highest number of customers

show products with low stock
```

---

# Built-In Commands

### View Schema

```text
:schema
```

### View History

```text
:history
```

### Export Results

```text
:export output.csv
```

### Execute Raw SQL

```text
:sql SELECT * FROM customers;
```

### Exit

```text
:quit
```

---

# Core Components

## Schema Loader

Responsibilities:

- Detect tables
- Detect columns
- Generate schema context
- Display schema information

---

## NL2SQL Engine

Responsibilities:

- Load T5 model
- Build prompt
- Generate SQL
- Apply post-processing

---

## Clarifier

Handles ambiguous queries:

Example:

```text
show recent orders
```

Follow-up:

```text
How recent?
1. Last 7 Days
2. Last 30 Days
3. Last 3 Months
```

---

## Database Executor

Responsibilities:

- Validate SQL
- Execute queries
- Handle errors
- Return structured results

---

## Renderer

Uses Rich Library:

- Syntax highlighted SQL
- Tables
- Panels
- Error messages

---
