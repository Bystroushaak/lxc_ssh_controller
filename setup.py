#! /usr/bin/env python3
from setuptools import setup
from setuptools import find_packages


changelog = open('CHANGELOG.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


def get_version(data):
    def all_same(s):
        return all(x == s[0] for x in s)

    def has_digit(s):
        return any(x.isdigit() for x in s)

    data = data.splitlines()
    return list(
        line for line, underline in zip(data, data[1:])
        if (len(line) == len(underline) and
            all_same(underline) and
            has_digit(line) and
            "." in line),
    )[0]


setup(
    name='',
    version=get_version(changelog),
    description="",
    long_description=long_description,
    # url='',  # TODO: !

    author='ComSource',
    author_email='bystrousak@kitakitsune.org',

    classifiers=[
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",

        "License :: Other/Proprietary License",
    ],
    license='© ComSource 2016',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    # namespace_packages=['',],

    zip_safe=False,
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),

    # test_suite='py.test',
    # tests_require=["pytest"],
    # extras_require={
    #     "test": [
    #         "pytest",
    #     ],
    #     "docs": [
    #         "sphinx",
    #         "sphinxcontrib-napoleon",
    #     ]
    # },
)
