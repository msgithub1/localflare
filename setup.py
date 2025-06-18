from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    fh.close()

setup(
    name="localflare",
    version="0.1.0",
    author="TianmuTNT",
    author_email="admin@astrarails.org",
    description="A lightweight desktop application development framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TianmuTNT/localflare",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "flask>=2.0.0",
        "pywebview>=3.0.0",
        "requests>=2.25.0",
        "werkzeug>=2.0.0",
    ],
) 