"""Configuration settings for core/security module"""
import os

SECURITY_DEBUG = os.getenv("SECURITY_DEBUG", "false").lower() == "true"
SECURITY_CONFIG_PROFILE = "Standard"
