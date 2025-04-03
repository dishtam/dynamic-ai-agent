import os
import yaml
import requests
import subprocess
from dotenv import load_dotenv
from utils.inspire import REFERENCE_YAML  # Import the reference pipeline

def load_env_variables():
    """Loads environment variables from .env file."""
    load_dotenv()
    return {
        "OLLAMA_API_URL": os.getenv("OLLAMA_API_URL"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL")
    }

def detect_language_and_version(source_code_path):
    """Detects the project's primary programming language and version."""
    os.chdir(source_code_path)  # Switch to the source code directory

    if os.path.exists("requirements.txt"):
        python_version = subprocess.run(["python", "--version"], capture_output=True, text=True)
        return "Python", python_version.stdout.strip() if python_version.returncode == 0 else "3.x"
    
    elif os.path.exists("package.json"):
        node_version = subprocess.run(["node", "--version"], capture_output=True, text=True)
        return "Node.js", node_version.stdout.strip().replace("v", "") if node_version.returncode == 0 else "18.x"
    
    elif os.path.exists("pom.xml"):
        return "Java", "17"
    
    elif os.path.exists("go.mod"):
        go_version = subprocess.run(["go", "version"], capture_output=True, text=True)
        return "Go", go_version.stdout.strip().split(" ")[2] if go_version.returncode == 0 else "1.18"
    
    elif os.path.exists("Cargo.toml"):
        return "Rust", "latest"

    return "Unknown", "latest"

def read_jobs_file(filepath):
    """Reads the jobs.txt file."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return file.read().strip()
    return ""

def validate_yaml(yaml_content):
    """Validates whether the generated content is a proper YAML structure."""
    try:
        yaml.safe_load(yaml_content)
        return True
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML format: {e}")
        return False

def clean_yaml(yaml_content):
    """Cleans up the YAML response by removing Markdown-style formatting."""
    yaml_content = yaml_content.strip()
    if yaml_content.startswith("```"):
        yaml_content = yaml_content.split("\n", 1)[-1]  # Remove first line
    if yaml_content.endswith("```"):
        yaml_content = yaml_content.rsplit("\n", 1)[0]  # Remove last line
    return yaml_content.strip()

def generate_ci_cd_pipeline(source_code_path):
    """Generates a GitHub Actions CI/CD pipeline for the given source code path."""
    env_vars = load_env_variables()
    
    # Detect language and version for the given project
    language, version = detect_language_and_version(source_code_path)
    
    # Read the job definitions if available
    jobs_file_path = os.path.join(source_code_path, 'jobs.txt')
    jobs_content = read_jobs_file(jobs_file_path)

    print(f"📌 Detected Language: {language} | Version: {version}")
    print(f"📂 Processing Source Code Path: {source_code_path}")

    prompt_text = f"""
    Generate a GitHub Actions workflow YAML file for a CI/CD pipeline.
    The workflow should follow this reference format:
    {REFERENCE_YAML}

    The workflow should:
    - Run on push and pull request events for main and dev branches.
    - Include predefined jobs such as code checkout and environment setup.
    - Dynamically set up the environment for {language} (version {version}).
    - Use appropriate package managers (e.g., pip for Python, npm for Node.js).
    - Dynamically incorporate the following user-defined jobs:
    {jobs_content if jobs_content else 'No additional jobs provided.'}

    Return only the YAML content without any extra text.
    """

    payload = {
        "model": env_vars["OLLAMA_MODEL"],
        "prompt": prompt_text,
        "stream": False
    }

    response = requests.post(env_vars["OLLAMA_API_URL"], json=payload)

    if response.status_code == 200:
        response_data = response.json()
        generated_yaml = response_data.get("response", "").strip()
        cleaned_yaml = clean_yaml(generated_yaml)

        if cleaned_yaml and validate_yaml(cleaned_yaml):
            workflow_dir = os.path.join(source_code_path, ".github/workflows")
            workflow_file = os.path.join(workflow_dir, "CI3.yml")

            os.makedirs(workflow_dir, exist_ok=True)

            with open(workflow_file, "w", encoding="utf-8") as f:
                f.write(cleaned_yaml + "\n")

            print(f"✅ CI/CD pipeline successfully generated and saved to {workflow_file}")
            return True
        else:
            print("❌ No valid YAML content generated.")
    else:
        print(f"❌ Failed to generate CI/CD pipeline. Status code: {response.status_code}")

    return False
