"""Configuration settings for core/tasks module"""
import os

TASKS_DEBUG = os.getenv("TASKS_DEBUG", "false").lower() == "true"
TASKS_CONFIG_PROFILE = "Standard"
