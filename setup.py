"""Setup script for Qwen-Assist-2."""

from setuptools import setup, find_packages

setup(
    name="qwen-assist-2",
    version="0.1.0",
    description="Multi-agent system built on the Qwen3 LLM",
    author="Qwen-Assist Team",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "qwen-agent[gui,rag,code_interpreter,mcp]>=0.0.1",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.0",
        "gradio>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "mypy>=1.5.1",
            "ruff>=0.0.290",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)