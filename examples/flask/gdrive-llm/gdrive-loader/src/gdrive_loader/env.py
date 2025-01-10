from pathlib import Path
import base64
import argparse
import sys
from typing import Dict


def load_env() -> Dict[str, str]:
    """Load .env file if it exists, return empty dict otherwise"""
    env_path = Path(".env")
    if not env_path.exists():
        return {}

    env_vars = {}
    for line in env_path.read_text().splitlines():
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            env_vars[key.strip()] = value.strip()

    return env_vars


def encode_credentials() -> str:
    """Encode credentials.json as base64"""
    path_to_credentials = Path("credentials.json")
    if not path_to_credentials.exists():
        print("Error: credentials.json file not found")
        print(
            "Please download your Google OAuth credentials and save them as credentials.json"
        )
        sys.exit(1)

    content = path_to_credentials.read_bytes()
    return base64.b64encode(content).decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description="Configure environment variables")
    parser.parse_args()

    env_vars = load_env()
    missing = []

    if "OPENAI_API_KEY" not in env_vars:
        missing.append("OPENAI_API_KEY")
        print("Enter your OpenAI API key:")
        api_key = input().strip()
        env_vars["OPENAI_API_KEY"] = api_key

    if "GOOGLE_CREDENTIALS_BASE64" not in env_vars:
        missing.append("GOOGLE_CREDENTIALS_BASE64")
        encoded = encode_credentials()
        env_vars["GOOGLE_CREDENTIALS_BASE64"] = encoded

    if missing:
        env_content = "\n".join(f"{k}={v}" for k, v in env_vars.items())
        Path(".env").write_text(env_content)
        print(f"Updated .env file with: {', '.join(missing)}")
    else:
        print("All required environment variables are already configured")


if __name__ == "__main__":
    main()
