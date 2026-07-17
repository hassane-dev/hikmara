"""Configuration settings for core/communication module"""
import os

COMMUNICATION_DEBUG = os.getenv("COMMUNICATION_DEBUG", "false").lower() == "true"
COMMUNICATION_CONFIG_PROFILE = "Standard"
