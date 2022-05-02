from setuptools import setup

setup(
    name="issnpy",
    version="0.1.0",
    author="Donatus Herre",
    author_email="donatus.herre@slub-dresden.de",
    description="ISSN Portal LD Client",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    license="GPLv3",
    url="https://github.com/herreio/issnpy",
    packages=["issnpy"],
    install_requires=["requests", "python-stdnum"],
    entry_points={
      'console_scripts': ['ISSN = issnpy.__main__:main'],
    },
)
