from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tableau-mcp-kartik",
    version="1.0.0",
    author="Tableau MCP Team",
    description="Model Context Protocol server for automated Tableau workbook generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kar10arora/TABLEAU_MCP",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'tableau-mcp=tableau_mcp.mcp.server:main',
        ],
    },
    package_data={
        'tableau_mcp': ['templates/*.twb'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastmcp>=0.2.0",
        "pandas>=2.0.0",
        "lxml>=4.9.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "google-generativeai>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
)
