from setuptools import setup, find_packages

setup(
    name="module_5",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "sqlalchemy",
        "psycopg2-binary",
        "python-dotenv",
        "requests",
        "beautifulsoup4",
    ],
)