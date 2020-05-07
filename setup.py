import setuptools

with open("Readme.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ncoreparser",
    version="0.0.7",
    author="Aron Radics",
    author_email="radics.aron.jozsef@gmail.com",
    description="Package to download from ncore.cc",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/radaron/ncoreparser",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=[
          'requests==2.23.0',
    ],
    python_requires='>=3.5',
)
