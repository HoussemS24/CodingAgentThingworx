"""Setup script for ThingWorx Coding Agent"""

from setuptools import setup, find_packages

setup(
    name="twx-agent",
    version="1.0.0",
    description="ThingWorx Coding Agent with RAG and safety guardrails",
    author="ThingWorx Development Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "jsonschema>=4.20.0",
        "click>=8.1.7",
        "rich>=13.7.0",
        "openai>=1.0.0",
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
    ],
    entry_points={
        "console_scripts": [
            "twx-agent=src.cli.main:cli",
        ],
    },
    python_requires=">=3.8",
)
