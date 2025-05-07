from setuptools import setup, find_packages

setup(
    name="ape-core",
    version="1.0.0",
    description="Core functionality for the Agentic Pipeline Engine (APE) system",
    author="APE Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pymysql>=1.0.2",
        "boto3>=1.26.0",
        "python-dotenv>=0.21.0",
    ],
    python_requires=">=3.8",
)