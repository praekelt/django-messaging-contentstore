from setuptools import setup, find_packages

setup(
    name="messaging_contentstore",
    version="0.1.3",
    url='http://github.com/praekelt/django-messaging-contentstore',
    license='None',
    description="A client library for the Messaging Content store HTTP \
                Services APIs",
    long_description=open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekeltfoundation.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
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
