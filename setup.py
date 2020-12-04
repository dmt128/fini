import setuptools, os
from setuptools.command.install import install
from fini import version

class CustomInstallCommand(install):
    """Customized setuptools install command - prints a friendly greeting."""
    def run(self):
        install.run(self)
        print("Custom install command called!")
        

class CustomDevelopCommand(install):
    """Customized setuptools install command - prints a friendly greeting."""
    def run(self):
        install.run(self)
        print("Custom develop command called!")
        

with open("README.md", "r") as fh:
    long_description = fh.read()

# # Force setuptools to recognize that this is a binary distribution
# # From: https://thomastrapp.com/blog/building-a-pypi-package-for-a-modern-cpp-project/
# class BinaryDistribution(setuptools.dist.Distribution):
#     @staticmethod
#     def has_ext_modules():
#         return True

# data = [os.listdir("fini"), os.listdir("fini/parser"), os.listdir("fini/termdef")]
# print(data)

setup_ = setuptools.setup(
    name="fini", # Replace with your own username
    version=version.__version__,
    author="Dimitris Zantalis",
    author_email="dzantalis@gmail.com",
    description="Gather financial information on publicly traded companies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    keywords=["fini"],
    packages=["fini", "fini.fonts", "fini.glossary", "fini.managers", "fini.providers", "fini.util"],
    platforms=["Linux", "Mac OSX"],
    test_suite="nose.collector",
    tests_require=["nose"],
    install_requires= ["colorama", "appdirs", "urllib3", "prompt_toolkit", "pytz", "tqdm"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    zip_safe=False,
    package_data={
        '.': ["LICENSE", "README.md"],
        'fini': os.listdir("fini"), 
        'fini.managers': ["base_config.json"], 
    },
    include_package_data=True,
    scripts=['scripts/fini', 'scripts/fint']
    # distclass=BinaryDistribution,
    # cmdclass={
    #     'install': CustomInstallCommand,
    #     'develop': CustomDevelopCommand,
    # },
)