#!/usr/bin/env python
"""
Utility script to set API keys for the text generation examples.

This script helps users set up their API keys for testing the text generation
functionality without having to modify environment variables manually.

Usage:
    python -m src.ai.text_generation.examples.set_api_key
"""
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

# Storage file for keys (stored in user's home directory)
API_KEYS_FILE = Path.home() / ".interview_platform_api_keys.json"


def load_api_keys():
    """Load saved API keys from file if it exists."""
    if API_KEYS_FILE.exists():
        try:
            with open(API_KEYS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_api_keys(keys):
    """Save API keys to file."""
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)
    # Set file permissions to only be readable by the owner
    os.chmod(API_KEYS_FILE, 0o600)
    print(f"Keys saved to {API_KEYS_FILE}")


def set_provider_key(provider, key_name, keys):
    """Set an API key for a specific provider."""
    print(f"\n=== Setting {provider.title()} API Key ===")
    current_key = keys.get(key_name, "")
    if current_key:
        print(f"Current key: {current_key[:4]}...{current_key[-4:] if len(current_key) > 8 else ''}")
        if input("Do you want to update this key? (y/n): ").lower() != "y":
            return
    
    new_key = input(f"Enter your {provider.title()} API key: ").strip()
    if new_key:
        keys[key_name] = new_key
        print(f"{provider.title()} API key updated.")
    else:
        print("No key entered. Keeping existing key.")


def set_default_provider(keys):
    """Set the default LLM provider."""
    print("\n=== Setting Default Provider ===")
    current = keys.get("LLM_PROVIDER", "perplexity")
    print(f"Current default provider: {current}")
    
    options = ["perplexity", "huggingface"]
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    choice = input(f"Select default provider (1-{len(options)}, or enter to keep current): ").strip()
    if choice and choice.isdigit() and 1 <= int(choice) <= len(options):
        keys["LLM_PROVIDER"] = options[int(choice) - 1]
        print(f"Default provider set to {keys['LLM_PROVIDER']}")


def main():
    """Main function to set up API keys."""
    print("=== AI Interview Platform API Key Setup ===")
    print("This utility helps you set up API keys for text generation services.")
    print("Keys will be saved to:", API_KEYS_FILE)

    # Load existing keys
    keys = load_api_keys()
    
    # Set keys for each provider
    set_provider_key("perplexity", "PERPLEXITY_API_KEY", keys)
    set_provider_key("hugging face", "HUGGINGFACE_API_KEY", keys)
    
    # Set default provider
    set_default_provider(keys)
    
    # Save updated keys
    save_api_keys(keys)
    
    print("\n=== Setup Complete ===")
    print("To use these keys in your environment, run the following commands:")
    for key, value in keys.items():
        if key != "LLM_PROVIDER":  # Skip non-API keys
            print(f"export {key}='{value}'")
    
    if "LLM_PROVIDER" in keys:
        print(f"export LLM_PROVIDER='{keys['LLM_PROVIDER']}'")
    
    print("\nOr for convenience, you can source the generated script:")
    print(f"source {API_KEYS_FILE.parent / 'interview_platform_env.sh'}")
    
    # Create a shell script for easier loading
    with open(API_KEYS_FILE.parent / "interview_platform_env.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# Generated environment variables for AI Interview Platform\n\n")
        for key, value in keys.items():
            f.write(f"export {key}='{value}'\n")
    
    # Set execute permissions for the script
    os.chmod(API_KEYS_FILE.parent / "interview_platform_env.sh", 0o700)


if __name__ == "__main__":
    main() 