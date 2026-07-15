from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="probe",
    version="1.0.0",
    author="Sharifeh Fadaei",
    author_email="sharifeh.fadaei@example.com",
    description="Production reliability evaluator for agentic systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sharifeh-fadaei/production-readiness-evaluator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.10",
    install_requires=[
        "langchain>=0.1.0",
        "langgraph>=0.0.20",
        "pydantic>=2.0.2",
        "pytest>=7.4.0",
        "python-dotenv>=1.0.0",
        "langfuse>=4.14.0",
        "requests>=2.31.0",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
],
)