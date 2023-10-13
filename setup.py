from setuptools import setup

setup(
    name="vsslite",
    version="0.3.0",
    url="https://github.com/uezo/vsslite",
    author="uezo",
    author_email="uezo@uezo.net",
    maintainer="uezo",
    maintainer_email="uezo@uezo.net",
    description="A vector similarity search engine on SQLite.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["numpy==1.26.0", "openai==0.28.1", "sqlite-vss==0.1.2", "fastapi==0.103.2", "uvicorn==0.23.2", "aiofiles==23.2.1"],
    license="MIT",
    packages=["vsslite"],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
