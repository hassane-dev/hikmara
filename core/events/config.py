"""Configuration settings for core/events module"""
import os

EVENTS_DEBUG = os.getenv("EVENTS_DEBUG", "false").lower() == "true"
EVENTS_CONFIG_PROFILE = "Standard"
