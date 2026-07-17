"""Configuration settings for core/configuration module"""
import os

CONFIGURATION_DEBUG = os.getenv("CONFIGURATION_DEBUG", "false").lower() == "true"
CONFIGURATION_CONFIG_PROFILE = "Standard"
