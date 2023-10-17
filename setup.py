import sys
from setuptools import setup

install_requires=[
    "openai==0.28.1",
    "fastapi==0.103.2",
    "uvicorn==0.23.2",
    "aiofiles==23.2.1",
    "langchain==0.0.314",
    "pdfminer.six==20221105",
    "chromadb==0.4.14",
    "tiktoken==0.5.1",
    "jq==1.6.0",
    "numpy==1.26.0",
    "sqlite-vss==0.1.2"
]
if sys.platform.startswith("linux"):
    # ChromaDB requirement
    install_requires.append("pysqlite3-binary==0.5.2.post1")
else:
    print("skip installing pysqlite3-binary")

setup(
    name="vsslite",
    version="0.5.0",
    url="https://github.com/uezo/vsslite",
    author="uezo",
    author_email="uezo@uezo.net",
    maintainer="uezo",
    maintainer_email="uezo@uezo.net",
    description="A vector similarity search engine for humans🥳",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    license="MIT",
    packages=["vsslite"],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
