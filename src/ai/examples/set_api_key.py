#!/usr/bin/env python
"""
Helper script to set the Perplexity API key in your .env file.

Usage:
    python -m src.ai.examples.set_api_key YOUR_API_KEY_HERE
"""
import os
import sys
from pathlib import Path


def update_env_file(api_key: str):
    """Update the .env file with the Perplexity API key."""
    # Get the project root directory
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    env_file = project_root / ".env"
    
    # Check if .env file exists
    if not env_file.exists():
        print(f"Error: .env file not found at {env_file}")
        print("Creating a new .env file...")
        with open(env_file, "w") as f:
            f.write("# AI Interview Simulation Platform - Environment Variables\n\n")
            f.write("# AI Provider Settings\n")
            f.write(f"PERPLEXITY_API_KEY={api_key}\n")
        print(f"Created new .env file with Perplexity API key")
        return True
    
    # Read the current .env file
    with open(env_file, "r") as f:
        lines = f.readlines()
    
    # Process the lines
    new_lines = []
    api_key_added = False
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            new_lines.append(line)
            continue
        
        # Check if the line is a comment
        if line.strip().startswith("#"):
            new_lines.append(line)
            continue
        
        # Update or add the PERPLEXITY_API_KEY
        if line.strip().startswith("PERPLEXITY_API_KEY="):
            new_lines.append(f"PERPLEXITY_API_KEY={api_key}\n")
            api_key_added = True
        else:
            new_lines.append(line)
    
    # If PERPLEXITY_API_KEY wasn't found, add it to the end
    if not api_key_added:
        # Add a section comment if it doesn't exist
        if not any("AI Provider Settings" in line for line in lines):
            new_lines.append("\n# AI Provider Settings\n")
        new_lines.append(f"PERPLEXITY_API_KEY={api_key}\n")
    
    # Write the updated .env file
    with open(env_file, "w") as f:
        f.writelines(new_lines)
    
    print(f"Successfully updated .env file with Perplexity API key")
    return True


def main():
    """Main function to run the script."""
    # Check if API key is provided as command-line argument
    if len(sys.argv) < 2:
        print("Error: Please provide your Perplexity API key as a command-line argument")
        print("Usage: python -m src.ai.examples.set_api_key YOUR_API_KEY_HERE")
        return 1
    
    # Get the API key from command-line argument
    api_key = sys.argv[1]
    
    # Update the .env file
    if update_env_file(api_key):
        print("You can now run the example script to test the LLM:")
        print("python -m src.ai.examples.llm_example")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main()) 