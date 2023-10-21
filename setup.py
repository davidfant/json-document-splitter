from setuptools import setup, find_packages

setup(
  name="json_document_splitter",
  version="0.0.1",
  author="David Fant",
  author_email="david@fant.io",
  description="A Python library for splitting JSON documents into even chunks.",
  long_description=open("README.md", "r").read(),
  long_description_content_type="text/markdown",
  url="https://github.com/davidfant/json-document-splitter",
  packages=find_packages(),
  python_requires='>=3.10',
)
