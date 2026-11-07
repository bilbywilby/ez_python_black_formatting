import os


class Config:
    """Configuration class for storing sensitive information."""

    def __init__(self):
        """Initialize the configuration with environment variables."""
        self.DB_CONNECTION_STRING = self.get_env_variable(
            'DB_CONNECTION_STRING')
        self.SMTP_SERVER = self.get_env_variable('SMTP_SERVER')
        self.SMTP_PORT = int(self.get_env_variable('SMTP_PORT', '587'))
        self.EMAIL_ADDRESS = self.get_env_variable('EMAIL_ADDRESS')
        self.EMAIL_PASSWORD = self.get_env_variable('EMAIL_PASSWORD')
        self.API_KEY = self.get_env_variable('API_KEY')

    @staticmethod
    def get_env_variable(name, default=None):
        """Get an environment variable or return a default value."""
        try:
            return os.environ[name]
        except KeyError:
            if default is not None:
                return default
            else:
                raise EnvironmentError(
                    f"The required environment variable {name} is not set.")


# Create a config object that can be imported in other modules
config = Config()
