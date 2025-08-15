# 🌐 Port Scanner

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Security](https://img.shields.io/badge/Security-Network%20Scanning-red.svg)]()
[![Tests](https://img.shields.io/badge/Tests-Pytest-green.svg)]()

## 📌 Overview

A fast and lightweight TCP port scanner built in Python. Designed for quick reconnaissance and automated network testing.

## 🚀 Features

- Scan single or multiple IP addresses
- Adjustable timeout and thread count
- Export scan results to `result.txt`
- Works on Linux, macOS, and Windows

## 📂 Project Structure

Port-Scanner/
│── scanner.py # Main port scanning script
│── tests/ # Automated test cases
│── result.txt # Sample output
│── requirements.txt
│── README.md


## 🧪 Automated Testing

pytest

🖥 Sample Output

[2025-08-15 12:10:00] Scanning target: 192.168.0.1
Open ports: 22, 80, 443
Scan completed in 2.35s

⚙ Installation

git clone https://github.com/Henil994/Port-Scanner.git
cd Port-Scanner
pip install -r requirements.txt
python scanner.py
