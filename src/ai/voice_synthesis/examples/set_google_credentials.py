#!/usr/bin/env python
"""
Helper script to set up Google Cloud credentials for voice synthesis.

This script guides users through the process of setting up Google Cloud credentials
for use with the voice synthesis service.

Usage:
    python -m src.ai.voice_synthesis.examples.set_google_credentials
"""
import os
import json
import sys
from pathlib import Path


def set_credentials_path():
    """Set the GOOGLE_APPLICATION_CREDENTIALS environment variable."""
    print("=" * 80)
    print("Google Cloud Text-to-Speech API Credentials Setup")
    print("=" * 80)
    print("\nThis script helps you set up Google Cloud credentials for the voice synthesis service.")
    print("\nTo use Google Cloud Text-to-Speech, you need:")
    print("1. A Google Cloud account")
    print("2. A project with the Text-to-Speech API enabled")
    print("3. A service account key (JSON file)")
    print("\nIf you don't have these yet, follow these steps:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Cloud Text-to-Speech API")
    print("4. Create a service account and download the JSON key file")
    print("\nFor detailed instructions, visit:")
    print("https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries")
    
    print("\n" + "=" * 80)
    
    # Ask user for the path to their credentials file
    credentials_path = input("\nEnter the path to your Google Cloud credentials JSON file: ")
    credentials_path = os.path.expanduser(credentials_path)
    
    if not os.path.exists(credentials_path):
        print(f"\nError: The file at {credentials_path} does not exist.")
        return False
    
    # Validate that it's a proper JSON file with expected fields
    try:
        with open(credentials_path, 'r') as f:
            credentials = json.load(f)
        
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        for field in required_fields:
            if field not in credentials:
                print(f"\nError: The JSON file is missing the required field '{field}'.")
                return False
        
        # Check if it's a service account key
        if credentials.get("type") != "service_account":
            print("\nError: The JSON file is not a service account key.")
            return False
        
        print(f"\nSuccessfully validated credentials for project: {credentials['project_id']}")
        
    except json.JSONDecodeError:
        print(f"\nError: The file at {credentials_path} is not a valid JSON file.")
        return False
    except Exception as e:
        print(f"\nError validating credentials: {e}")
        return False
    
    # Set the environment variable
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    print(f"\nSet GOOGLE_APPLICATION_CREDENTIALS={credentials_path}")
    
    # Suggest adding to shell profile
    shell_profile = None
    if os.name == "posix":  # Unix-like systems
        if "SHELL" in os.environ:
            shell = os.path.basename(os.environ["SHELL"])
            if shell == "bash":
                shell_profile = "~/.bashrc or ~/.bash_profile"
            elif shell == "zsh":
                shell_profile = "~/.zshrc"
            elif shell == "fish":
                shell_profile = "~/.config/fish/config.fish"
    
    if shell_profile:
        print("\nTo make this permanent, add the following line to your", shell_profile)
        print(f'export GOOGLE_APPLICATION_CREDENTIALS="{credentials_path}"')
    
    # Ask if user wants to save to .env file
    save_to_env = input("\nWould you like to save this to your project's .env file? (y/n): ").lower()
    if save_to_env == 'y':
        # Determine the location of the .env file
        project_root = Path(__file__).resolve().parents[4]  # Go up 4 levels from this script
        env_file = project_root / ".env"
        
        # Read existing .env file if it exists
        env_lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_lines = f.readlines()
        
        # Remove any existing GOOGLE_APPLICATION_CREDENTIALS line
        env_lines = [line for line in env_lines if not line.startswith("GOOGLE_APPLICATION_CREDENTIALS=")]
        
        # Add the new line
        env_lines.append(f'GOOGLE_APPLICATION_CREDENTIALS="{credentials_path}"\n')
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.writelines(env_lines)
        
        print(f"\nUpdated {env_file} with your Google Cloud credentials path.")
    
    print("\nSetup complete! You can now use the Google Cloud Text-to-Speech API.")
    return True


def test_credentials():
    """Test if the credentials work by checking if we can list voices."""
    try:
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            print("\nError: GOOGLE_APPLICATION_CREDENTIALS is not set.")
            return False
        
        print(f"\nTesting credentials from: {credentials_path}")
        
        # Import the Google Cloud client library after setting credentials
        from google.cloud import texttospeech
        
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()
        
        # List available voices
        response = client.list_voices()
        voices = response.voices
        
        if voices:
            print(f"\nSuccess! Found {len(voices)} available voices.")
            print("Your Google Cloud Text-to-Speech credentials are working correctly.")
            return True
        else:
            print("\nWarning: Credentials seem valid but no voices were found.")
            return False
            
    except Exception as e:
        print(f"\nError testing credentials: {e}")
        return False


if __name__ == "__main__":
    if set_credentials_path():
        test_credentials()
    else:
        print("\nCredential setup failed. Please try again.")
        sys.exit(1) 