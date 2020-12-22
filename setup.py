import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="zscalertools",
  version="0.0.4",
  author="Bryce Myers",
  author_email="bdmyers@mmm.com",
  description="Zscaler Tools",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.mmm.com/network-automation/zscalertools",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  install_requires=[
    'requests',
  ],
  python_requires='>=3.6',
)