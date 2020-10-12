import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="new-flask-app",
    version="1.0.2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skyjung/hackmit",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    license="MIT",
    install_requires=["PyInquirer", "jinja2"],
    
)