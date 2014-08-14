import setuptools


# =====
if __name__ == "__main__":
    setuptools.setup(
        name="contextlog",
        version="0.4",
        url="https://github.com/yandex-sysmon/contextlog",
        license="LGPLv3",
        author="Devaev Maxim",
        author_email="mdevaev@gmail.com",
        description="Context-based logger and formatters collection",
        platforms="any",

        packages=[
            "contextlog",
        ],

        classifiers=[  # http://pypi.python.org/pypi?:action=list_classifiers
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: System :: Logging",
        ],
    )
