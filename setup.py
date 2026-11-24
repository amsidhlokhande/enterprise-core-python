"""
Setup script for enterprise-core-python.
Enables standard pip install -e . and wheel packaging with centralized dependency versions.
"""
from setuptools import setup, find_packages

setup(
    name="enterprise-core-python",
    version="1.0.0",
    packages=find_packages(include=["enterprise_core", "enterprise_core.*"]),
    install_requires=[
        "Flask==3.1.0",
        "werkzeug==3.1.3",
        "python-json-logger==2.0.7",
        "requests==2.32.3",
        "urllib3==2.2.3",
        "gunicorn==23.0.0",
        "waitress==3.0.1",
        "pytest==8.3.3",
    ],
    extras_require={
        "aws": ["boto3==1.35.40"],
    },
    python_requires=">=3.10",
)
