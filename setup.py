from setuptools import setup, find_packages

setup(
    name="django-messaging-contentstore",
    version="0.1.3",
    url="https://github.com/praekelt/django-messaging-contentstore",
    license='BSD',
    description=(
        "A RESTful API for managing collections of messaging content"),
    long_description=open('README.rst', 'r').read(),
    author='Western Cape Labs',
    author_email='devops@westerncapelabs.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django==1.8',
        'djangorestframework',
        'django-filter'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
)
