# 🐍 Python Environment Setup Guide

## 🔄 Install or Upgrade pip

Before installing project dependencies, ensure you have the latest version of `pip`.

### 📥 Install pip (if not already installed)

If `pip` is missing, you can install it using Python’s built-in module:

python -m ensurepip --upgrade

### Afternatively download and run the official installer

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

### ⬆️ Upgrade pip to the Latest Version

python -m pip install --upgrade pip


This project uses a virtual environment and a `requirements.txt` file to manage dependencies. Follow the steps below to get started.

---

## 📦 Step 1: Create a Virtual Environment

Use Python's built-in `venv` module to create an isolated environment:

python -m venv venv

---

## ⚡ Step 2: Activate the Virtual Environment

source venv/bin/activate

---

## 📜 Step 3: Install Dependencies

pip install -r requirements.txt

---

## ✅ Step 4: Verify Installation

pip list

---