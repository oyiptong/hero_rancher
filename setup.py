from setuptools import setup, find_packages

setup(
    name="hero_rancher",
    url="herorancher.com",
    version="1.0.0",
    description="Fire Emblem Heroes Rancher",
    author="Olivier Yiptong",
    author_email="olivier@olivieryiptong.com",
    packages=find_packages(),
    scripts=["scripts/manage.py"])
