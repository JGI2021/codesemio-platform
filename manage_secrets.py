#!/usr/bin/env python3
"""
Secret Management CLI for CodeSemio Platform
Manages credentials using 1Password for both local and Docker environments
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from secrets_manager import get_secrets_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_1password():
    """Guide user through 1Password CLI setup"""
    print("\n🔐 1Password CLI Setup Guide")
    print("=" * 50)
    print("\n1. Install 1Password CLI (if not already installed):")
    print("   macOS: brew install --cask 1password-cli")
    print("   Linux: https://1password.com/downloads/command-line/")
    print("\n2. Sign in to 1Password:")
    print("   op signin")
    print("\n3. Create a vault called 'CodeSemio' in 1Password")
    print("\n4. Add the following items to the vault:")
    print("   - OpenAI API (with 'credential' field)")
    print("   - Anthropic API (with 'credential' field)")
    print("   - Mistral API (with 'credential' field)")
    print("   - MongoDB Atlas (with 'connection_string' field)")
    print("\n5. Run this script again with --check")
    print("=" * 50)


def check_secrets():
    """Check if all required secrets are available"""
    manager = get_secrets_manager()
    
    print("\n🔍 Checking Secrets Configuration")
    print("=" * 50)
    
    required_secrets = [
        ("MONGODB_URI", "MongoDB connection string"),
        ("OPENAI_API_KEY", "OpenAI API key"),
        ("ANTHROPIC_API_KEY", "Anthropic API key (optional)"),
        ("MISTRAL_API_KEY", "Mistral API key (optional)"),
        ("DB_NAME", "Database name"),
        ("DEFAULT_APP", "Default application"),
        ("DEFAULT_MODEL", "Default LLM model"),
    ]
    
    all_good = True
    for key, description in required_secrets:
        value = manager.get_secret(key)
        if value:
            # Show masked value
            if "KEY" in key or "URI" in key:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {key}: {masked} ({description})")
            else:
                print(f"✅ {key}: {value} ({description})")
        else:
            if "optional" in description.lower():
                print(f"⚠️  {key}: Not configured ({description})")
            else:
                print(f"❌ {key}: Missing ({description})")
                all_good = False
    
    print("=" * 50)
    if all_good:
        print("✅ All required secrets are configured!")
    else:
        print("❌ Some required secrets are missing. Please configure them.")
    
    return all_good


def export_docker_env(output_file: str = ".env.docker"):
    """Export secrets for Docker deployment"""
    manager = get_secrets_manager()
    
    print(f"\n📦 Exporting secrets for Docker to {output_file}")
    print("=" * 50)
    
    if manager.export_for_docker(output_file):
        print(f"✅ Secrets exported successfully to {output_file}")
        print("\n⚠️  IMPORTANT:")
        print(f"   - {output_file} contains sensitive data")
        print("   - DO NOT commit this file to Git")
        print("   - File permissions set to 600 (owner read/write only)")
        print("\n📋 To use with Docker:")
        print(f"   docker run --env-file {output_file} codesemio-platform")
        print("\n   Or in docker-compose.yml:")
        print(f"   env_file: {output_file}")
        return True
    else:
        print("❌ Failed to export secrets for Docker")
        return False


def create_docker_compose():
    """Create a Docker Compose file for local deployment"""
    compose_content = """version: '3.8'

services:
  codesemio-platform:
    build: .
    container_name: codesemio-platform
    env_file: .env.docker
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - codesemio-net
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  codesemio-net:
    driver: bridge

# Optional: Add MongoDB container for local development
# services:
#   mongodb:
#     image: mongo:7
#     container_name: codesemio-mongodb
#     environment:
#       MONGO_INITDB_ROOT_USERNAME: admin
#       MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
#     volumes:
#       - mongodb_data:/data/db
#     networks:
#       - codesemio-net
# 
# volumes:
#   mongodb_data:
"""
    
    compose_file = Path("docker-compose.yml")
    compose_file.write_text(compose_content)
    print(f"✅ Created {compose_file}")


def create_dockerfile():
    """Create a Dockerfile for the platform"""
    dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY *.py ./

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    dockerfile = Path("Dockerfile")
    dockerfile.write_text(dockerfile_content)
    print(f"✅ Created {dockerfile}")


def setup_docker_deployment():
    """Complete Docker deployment setup"""
    print("\n🐳 Setting up Docker Deployment")
    print("=" * 50)
    
    # Check secrets first
    if not check_secrets():
        print("\n❌ Please configure all required secrets first")
        return False
    
    # Export Docker env file
    if not export_docker_env():
        return False
    
    # Create Docker files
    create_dockerfile()
    create_docker_compose()
    
    # Update .gitignore
    gitignore_path = Path(".gitignore")
    gitignore_content = gitignore_path.read_text() if gitignore_path.exists() else ""
    
    additions = [".env.docker", "*.env.docker", ".env.local", "docker-compose.override.yml"]
    new_lines = []
    
    for item in additions:
        if item not in gitignore_content:
            new_lines.append(item)
    
    if new_lines:
        with gitignore_path.open("a") as f:
            f.write("\n# Docker secrets\n")
            for line in new_lines:
                f.write(f"{line}\n")
        print("✅ Updated .gitignore")
    
    print("\n📋 Docker Deployment Instructions:")
    print("=" * 50)
    print("\n1. Build the Docker image:")
    print("   docker-compose build")
    print("\n2. Start the platform:")
    print("   docker-compose up -d")
    print("\n3. View logs:")
    print("   docker-compose logs -f")
    print("\n4. Stop the platform:")
    print("   docker-compose down")
    print("\n5. Update secrets (when needed):")
    print("   python manage_secrets.py --export-docker")
    print("   docker-compose restart")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Manage secrets for CodeSemio Platform using 1Password"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Show 1Password setup instructions"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if all required secrets are configured"
    )
    parser.add_argument(
        "--export-docker",
        action="store_true",
        help="Export secrets for Docker deployment"
    )
    parser.add_argument(
        "--docker-setup",
        action="store_true",
        help="Complete Docker deployment setup"
    )
    parser.add_argument(
        "--output",
        default=".env.docker",
        help="Output file for Docker secrets (default: .env.docker)"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default="development",
        help="Environment to use (default: development)"
    )
    
    args = parser.parse_args()
    
    # Set environment
    import os
    os.environ["ENVIRONMENT"] = args.environment
    
    # Handle commands
    if args.setup:
        setup_1password()
    elif args.check:
        check_secrets()
    elif args.export_docker:
        export_docker_env(args.output)
    elif args.docker_setup:
        setup_docker_deployment()
    else:
        # Default: check secrets
        if check_secrets():
            print("\n💡 Tip: Use --docker-setup for complete Docker deployment")
        else:
            print("\n💡 Tip: Use --setup for 1Password configuration guide")


if __name__ == "__main__":
    main()