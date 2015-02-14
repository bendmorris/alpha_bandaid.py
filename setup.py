from setuptools import setup

setup(
    name='alpha_bandaid',
    py_modules=['alpha_bandaid'],
    entry_points={
        'console_scripts': ['alpha_bandaid = alpha_bandaid:main', ],
    },
)
