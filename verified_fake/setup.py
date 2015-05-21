from setuptools import setup

setup(
    name="fake-django-messaging-contentstore",
    version="0.1.3",
    url='http://github.com/praekelt/django-messaging-contentstore',
    license='BSD',
    description="A verified fake implementation of \
                django-messaging-contentstore for testing.",
    long_description=open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekeltfoundation.org',
    py_modules=[],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
