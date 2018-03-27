from setuptools import find_packages, setup
from chat import __version__

top_packages = [
    'chat',
    'tests',
]
packages_pattern = top_packages + [p + '.*' for p in top_packages]


with open('requirements.txt', encoding='utf-8') as fp:
    install_requires = [line.strip() for line in fp]


setup(name='chat',
      version=__version__,
      description='Yet another chat',
      author='Miroshnichenko Ilia',
      author_email='elias.mir@ro.ru',
      license='Apache-2.0',
      platforms=['POSIX'],
      packages=find_packages(),
      python_requires='>=3.6.2',
      include_package_data=True,
      install_requires=install_requires,
      zip_safe=False)
