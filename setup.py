from setuptools import setup, find_packages

setup(
    name='mitzeichner',
    version='0.1',
    description='',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://mitzeichner.pudo.org/',
    install_requires=[
        "lxml>=2.2.7",
        "Flask>=0.6.1"
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    entry_points="""
    """,
)
