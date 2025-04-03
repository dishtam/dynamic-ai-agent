REFERENCE_YAML = """\
name: Simple CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python
        if: ${{ hashFiles('requirements.txt') != '' }}
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"

      - name: Set up Node.js
        if: ${{ hashFiles('package.json') != '' }}
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install Dependencies
        run: |
          if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi
          if [ -f "package.json" ]; then npm install; fi

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Run Tests
        run: |
          if [ -f "requirements.txt" ]; then pytest; fi
          if [ -f "package.json" ]; then npm test; fi

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy Application
        run: echo "🚀 Deploying application..."
"""
