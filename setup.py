import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-worker",
    version="0.0.5",
    author="Dillon Bowen",
    author_email="dsbowen@wharton.upenn.edu",
    description="Flask-Worker simplifies interaction with a Redis Queue for executing long-running tasks in a Flask application.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dsbowen/flask-worker",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'bs4==0.0.1',
        'flask==1.1.1',
        'rq==1.2.0',
        'sqlalchemy==1.3.12',
        'sqallchemy-modelid==0.0.2',
        'sqlalchemy-mutable==0.0.7',
        'sqlalchemy-mutablesoup==0.0.5',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)