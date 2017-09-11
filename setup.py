import setuptools


# =====
if __name__ == "__main__":
    setuptools.setup(
        name="contextlog",
        version="1.0",
        url="https://github.com/mdevaev/contextlog",
        license="LGPLv3",
        author="Maxim Devaev",
        author_email="mdevaev@gmail.com",
        description="Context-based logger and formatters collection",
        platforms="any",

        packages=[
            "contextlog",
        ],

        install_requires=[
            "colorlog",
        ],

        classifiers=[  # http://pypi.python.org/pypi?:action=list_classifiers
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: System :: Logging",
        ],
    )
