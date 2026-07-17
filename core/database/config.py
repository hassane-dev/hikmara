"""Configuration settings for core/database module"""
import os

DATABASE_DEBUG = os.getenv("DATABASE_DEBUG", "false").lower() == "true"
DATABASE_CONFIG_PROFILE = "Standard"
