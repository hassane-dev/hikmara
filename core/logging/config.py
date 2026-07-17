"""Configuration settings for core/logging module"""
import os

LOGGING_DEBUG = os.getenv("LOGGING_DEBUG", "false").lower() == "true"
LOGGING_CONFIG_PROFILE = "Standard"
