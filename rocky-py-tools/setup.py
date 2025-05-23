from setuptools import setup, find_packages

setup(
    name="rockytools",
    version="0.1.0",
    description="Set of utilities with Rofi as front end",
    author="Rocky",
    author_email="rocky.0x4e@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'restmail = rockytools.restmail:main',
            'audioControl = rockytools.audioControl:main',
            'bluetoothControl = rockytools.bluetoothControl:main',
            'controlCenter = rockytools.controlCenter:main',
            'extDrive = rockytools.extDrive:main',
            'monitorControl = rockytools.monitorControl:main',
            'networkControl = rockytools.networkControl:main',
            'showRamStat = rockytools.showRamStat:main',
            'simpleNotepad = rockytools.simpleNotepad:main',
            'screenshot = rockytools.screenshot:main',
            'dunsthistory = rockytools.dunsthistory:main',
        ],
    },
    install_requires=[
        'requests',
        'psutil',
        'libtmux'
    ],
)
