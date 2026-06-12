from setuptools import setup, find_packages

setup(
    name="f-society-media",
    version="1.0.0",
    py_modules=["main"],
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
        "rich",
        "PySide6",
        "textual",
    ],
    entry_points={
        "console_scripts": [
            "fs=main:entry_point",
            "f-society=main:entry_point",
        ],
    },
    python_requires=">=3.7",
)
