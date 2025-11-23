"""
BridgeLink - Expose Android devices remotely via NativeBridge
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding='utf-8')
except FileNotFoundError:
    long_description = "CLI tool to expose Android devices remotely via NativeBridge"

setup(
    name="bridgelink",
    version="0.2.1",
    author="Himanshu Kukreja",
    author_email="kukreja.him@gmail.com",
    description="CLI tool to expose Android devices remotely via NativeBridge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AutoFlowLabs/bridgelink",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Emulators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "psutil>=5.9.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "bridgelink=bridgelink.cli:main",
        ],
    },
    include_package_data=True,
    keywords="android adb testing remote-devices nativebridge tunnel bore",
    project_urls={
        "Bug Reports": "https://github.com/AutoFlowLabs/bridgelink/issues",
        "Documentation": "https://github.com/AutoFlowLabs/bridgelink#readme",
        "Source": "https://github.com/AutoFlowLabs/bridgelink",
        "Changelog": "https://github.com/AutoFlowLabs/bridgelink/blob/main/CHANGELOG.md",
    },
)
