"""Config reader for ts-cf-dns."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Define the settings we need."""
    TAILSCALE_API_KEY: [str] = "your_tailscale_api_key"  # required
    TAILSCALE_TAILNET: [str] = "your_tailnet"  # required
    CLOUDFLARE_API_KEY: [str] = "your_cloudflare_api_key"  # required if using cloudflare, duh
    CLOUDFLARE_ZONE_ID: [str] = "your_cloudflare_zone_id"  # required if using cloudflare
    CLOUDFLARE_EMAIL: [str] = "your_email"  # required if using cloudflare
    DNS_DOMAIN: [str] = "example.com"  # Base domain for DNS records, required

    class Config:
        """Define our settings file."""
        env_file = ".env"


settings = Settings()