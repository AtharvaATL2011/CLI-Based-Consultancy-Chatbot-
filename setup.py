from setuptools import setup, find_packages

setup(
    name="multimind-chatbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.25.0",
        "rich>=13.7.0",
        "click>=8.1.7",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "multimind=chatbot.cli:main",
        ],
    },
)