"""
Secrets Manager for CodeSemio Platform
Integrates with 1Password for secure credential management
Supports both local development and Docker/Azure production environments
"""

import os
import json
import subprocess
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Manages secrets from multiple sources:
    1. 1Password (primary)
    2. Environment variables (fallback)
    3. .env file (development)
    """
    
    def __init__(self, vault_name: str = "CodeSemio", environment: str = "development"):
        """
        Initialize SecretsManager
        
        Args:
            vault_name: Name of the 1Password vault
            environment: Current environment (development/staging/production)
        """
        self.vault_name = vault_name
        self.environment = environment
        self.secrets_cache: Dict[str, Any] = {}
        self.op_available = self._check_op_cli()
        
        # Load .env file for development
        if environment == "development":
            env_path = Path(__file__).parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"Loaded .env file from {env_path}")
    
    def _check_op_cli(self) -> bool:
        """Check if 1Password CLI is available"""
        try:
            result = subprocess.run(
                ["op", "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info(f"1Password CLI available: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        
        logger.warning("1Password CLI not found. Falling back to environment variables.")
        return False
    
    def _get_from_1password(self, item_name: str, field: str = "password") -> Optional[str]:
        """
        Retrieve a secret from 1Password
        
        Args:
            item_name: Name of the item in 1Password
            field: Field to retrieve (default: password)
        
        Returns:
            Secret value or None if not found
        """
        if not self.op_available:
            return None
        
        try:
            # Construct the reference
            reference = f"op://{self.vault_name}/{item_name}/{field}"
            
            # Use op read command
            result = subprocess.run(
                ["op", "read", reference],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                value = result.stdout.strip()
                logger.debug(f"Retrieved {item_name} from 1Password")
                return value
            else:
                logger.warning(f"Failed to retrieve {item_name} from 1Password: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error accessing 1Password: {e}")
            return None
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret from available sources (1Password > env vars > default)
        
        Args:
            key: Secret key (e.g., 'OPENAI_API_KEY')
            default: Default value if secret not found
        
        Returns:
            Secret value or default
        """
        # Check cache first
        if key in self.secrets_cache:
            return self.secrets_cache[key]
        
        # Try 1Password
        if self.op_available:
            # Map common keys to 1Password items
            op_mapping = {
                "OPENAI_API_KEY": ("OpenAI API", "credential"),
                "ANTHROPIC_API_KEY": ("Anthropic API", "credential"),
                "MISTRAL_API_KEY": ("Mistral API", "credential"),
                "MONGODB_URI": ("MongoDB Atlas", "connection_string"),
                "AZURE_KEY_VAULT_URL": ("Azure Key Vault", "url"),
                "AZURE_CLIENT_ID": ("Azure Service Principal", "client_id"),
                "AZURE_CLIENT_SECRET": ("Azure Service Principal", "client_secret"),
                "AZURE_TENANT_ID": ("Azure Service Principal", "tenant_id"),
            }
            
            if key in op_mapping:
                item_name, field = op_mapping[key]
                value = self._get_from_1password(item_name, field)
                if value:
                    self.secrets_cache[key] = value
                    return value
        
        # Fallback to environment variables
        value = os.getenv(key, default)
        if value:
            self.secrets_cache[key] = value
            logger.debug(f"Using {key} from environment variables")
        else:
            logger.warning(f"Secret {key} not found in any source")
        
        return value
    
    def get_all_secrets(self) -> Dict[str, str]:
        """
        Get all required secrets for the application
        
        Returns:
            Dictionary of all secrets
        """
        required_secrets = [
            "MONGODB_URI",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "MISTRAL_API_KEY",
            "DB_NAME",
            "DEFAULT_APP",
            "DEFAULT_MODEL",
        ]
        
        secrets = {}
        for key in required_secrets:
            value = self.get_secret(key)
            if value:
                secrets[key] = value
        
        return secrets
    
    def export_for_docker(self, output_file: str = ".env.docker") -> bool:
        """
        Export secrets to a Docker env file for local Docker deployment
        
        Args:
            output_file: Path to output file (default: .env.docker)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            secrets = self.get_all_secrets()
            
            # Create Docker env file
            env_content = []
            env_content.append("# Generated Docker environment file from 1Password")
            env_content.append("# DO NOT COMMIT THIS FILE TO GIT\n")
            
            for key, value in secrets.items():
                # Escape special characters for Docker
                escaped_value = value.replace('"', '\\"')
                env_content.append(f'{key}="{escaped_value}"')
            
            # Write to file
            output_path = Path(output_file)
            output_path.write_text("\n".join(env_content))
            
            # Set restrictive permissions (only owner can read/write)
            os.chmod(output_path, 0o600)
            
            logger.info(f"Exported secrets to {output_file} for Docker")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export secrets for Docker: {e}")
            return False
    
    def setup_docker_secrets(self, container_name: str = "codesemio-platform") -> bool:
        """
        Setup secrets for running Docker container using docker exec
        
        Args:
            container_name: Name of the Docker container
        
        Returns:
            True if successful, False otherwise
        """
        try:
            secrets = self.get_all_secrets()
            
            for key, value in secrets.items():
                # Set environment variable in running container
                cmd = [
                    "docker", "exec", container_name,
                    "sh", "-c", f"export {key}='{value}'"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                
                if result.returncode != 0:
                    logger.warning(f"Failed to set {key} in Docker container: {result.stderr}")
            
            logger.info(f"Configured secrets in Docker container: {container_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Docker secrets: {e}")
            return False


# Singleton instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager(environment: Optional[str] = None) -> SecretsManager:
    """
    Get or create the singleton SecretsManager instance
    
    Args:
        environment: Override environment (development/staging/production)
    
    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    
    if _secrets_manager is None or (environment and environment != _secrets_manager.environment):
        env = environment or os.getenv("ENVIRONMENT", "development")
        _secrets_manager = SecretsManager(environment=env)
    
    return _secrets_manager


# Convenience functions
def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a secret using the default secrets manager"""
    return get_secrets_manager().get_secret(key, default)


def get_all_secrets() -> Dict[str, str]:
    """Get all secrets using the default secrets manager"""
    return get_secrets_manager().get_all_secrets()