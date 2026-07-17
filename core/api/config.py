"""Configuration settings for core/api module"""
import os

API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"
API_CONFIG_PROFILE = "Standard"
