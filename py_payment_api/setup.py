from setuptools import setup, find_packages

setup(
    name="@dclmonster/py-payment-api",
    version="0.1.0",
    description="Python Payment API with multiple payment providers",
    author="DclMonster",
    author_email="dev@dclmonster.com",
    url="https://github.com/DclMonster/ExtendablePaymentApi",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "flask-restful>=0.3.9",
        "pyjwt>=2.3.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pylint>=2.12.0",
            "twine>=4.0.0",
            "build>=0.10.0",
            # Documentation dependencies
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=2.0.0",
            "sphinx-markdown-builder>=0.6.0",
            "sphinx-autodoc-typehints>=1.25.0",
            "sphinx-autoapi>=3.0.0",
            "myst-parser>=2.0.0",
            "ghp-import>=2.1.0",
            "numpydoc>=1.6.0",
            "numpy>=1.24.0",
            "matplotlib>=3.7.0",
            # Docstring coverage
            "interrogate>=1.5.0",
            "docstr-coverage>=2.3.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 