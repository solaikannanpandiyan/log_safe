from setuptools import setup, find_packages

with open("pypi_readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="log_safe",
    version="0.1.2",
    author="Solaikannan Pandiyan",
    author_email="solaikannanpandiyan@gmail.com",  # Replace with your email
    description= "log_safe is a Python library that provides safe and efficient logging capabilities for multiprocessing applications. It ensures that logging is thread-safe and process-safe, making it ideal for complex, multi-process Python applications",
    long_description= long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/solaikannanpandiyan/log_safe",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
    ],
)