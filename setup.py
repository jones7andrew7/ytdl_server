from setuptools import find_packages, setup

setup(
    name='ytdl_server',
    version='1.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'youtube-dl',
        'configparser',
    ],
)
