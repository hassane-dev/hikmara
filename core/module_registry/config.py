"""Configuration settings for core/module_registry module"""
import os

MODULE_REGISTRY_DEBUG = os.getenv("MODULE_REGISTRY_DEBUG", "false").lower() == "true"
MODULE_REGISTRY_CONFIG_PROFILE = "Standard"
