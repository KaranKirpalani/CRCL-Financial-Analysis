from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="crcl-financial-analysis",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Comprehensive financial analysis of Circle Internet Group (CRCL)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/CRCL_Financial_Analysis",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/CRCL_Financial_Analysis/issues",
        "Documentation": "https://github.com/yourusername/CRCL_Financial_Analysis/blob/main/docs/",
        "Source Code": "https://github.com/yourusername/CRCL_Financial_Analysis",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "jupyter>=1.0.0",
        ],
        "visualization": [
            "plotly>=5.0.0",
            "seaborn>=0.11.0",
            "matplotlib>=3.4.0",
        ],
        "database": [
            "sqlalchemy>=1.4.0",
            "psycopg2-binary>=2.9.0",
            "pymysql>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crcl-analysis=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.json", "*.txt", "*.md"],
    },
    keywords="finance, financial-analysis, investment, dcf, valuation, stablecoin, circle, crcl",
    zip_safe=False,
)