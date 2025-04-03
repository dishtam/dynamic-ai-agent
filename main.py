import os
import yaml
from agents.ci_cd_agent import generate_ci_cd_pipeline

def get_source_code_path():
    """Detects the source code location from config.yaml or defaults to the current directory."""
    config_file = "config.yaml"

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
            return config.get("source_code_path", os.getcwd())
    
    return os.getcwd()

if __name__ == "__main__":
    source_code_path = get_source_code_path()
    print(f"📂 Detected Source Code Path: {source_code_path}")

    success = generate_ci_cd_pipeline(source_code_path)
    if success:
        print("🚀 Pipeline generation complete!")
    else:
        print("⚠️ Pipeline generation failed.")
