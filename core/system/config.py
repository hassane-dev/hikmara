"""Configuration settings for core/system module"""
import os

SYSTEM_DEBUG = os.getenv("SYSTEM_DEBUG", "false").lower() == "true"
SYSTEM_CONFIG_PROFILE = "Standard"
