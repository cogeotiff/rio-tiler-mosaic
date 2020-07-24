"""Setup for rio-tiler-mosaic."""

from setuptools import find_packages, setup

# Runtime requirements.
inst_reqs = ["rio-tiler~=2.0a"]

extra_reqs = {
    "test": ["pytest", "pytest-cov", "pytest-benchmark"],
    "dev": ["pytest", "pytest-cov", "pytest-benchmark", "pre-commit"],
}

with open("README.md") as f:
    long_description = f.read()

setup(
    name="rio-tiler-mosaic",
    version="0.0.1dev5",
    python_requires=">=3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description=u"""A rio-tiler plugin to create mosaic tiles.""",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords="COG Mosaic GIS",
    author=u"Vincent Sarago",
    author_email="vincent@developmentseed.org",
    url="https://github.com/cogeotiff/rio-tiler-mosaic",
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
