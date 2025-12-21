from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="real-time-fraud-detection",
    version="1.0.0",
    author="techdevworks",
    description="Production-grade real-time fraud detection using Kafka & Spark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/techdevworks/real-time-fraud-detection-streaming",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.9",
    install_requires=[
        "kafka-python>=2.0.2",
        "pyspark>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "flake8>=6.0",
            "black>=23.0",
        ],
        "spark": [
            "pyspark>=3.4.0",
            "delta-spark>=3.0.0",
        ],
    },
)
