from setuptools import setup, find_packages

setup(
    name='ecommerce-kentapay-plugin',
    version='0.1.0',
    description='Kentapay payment processor for Open edX Ecommerce',
    author='trigdev.tech',
    author_email='trigdev@technologies.com',
    url='https://github.com/omnisoft-technolofies/kentapay-plugin',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',  # For API calls to Kentapay
    ],
)
