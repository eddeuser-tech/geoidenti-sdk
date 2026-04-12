"""
Setup script for GeoIdenti Python SDK
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="geoidenti-sdk",
    version="1.0.0",
    author="GeoIdenti Team",
    author_email="sdk@geoidenti.com",
    description="Python SDK for GeoIdenti biometric and geospatial API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eddeuser-tech/geoidenti-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "flake8>=3.9.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/eddeuser-tech/geoidenti-sdk/issues",
        "Source": "https://github.com/eddeuser-tech/geoidenti-sdk",
        "Documentation": "https://geoidenti-sdk.readthedocs.io/",
    },
)
