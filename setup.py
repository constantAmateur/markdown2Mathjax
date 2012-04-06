from distutils.core import setup

setup(
    name="markdown2Mathjax",
    version="0.1.0",
    author="Matthew D. Young",
    author_email="matt.d.young@gmail.com",
    packages=["markdown2Mathjax","markdown2Mathjax.test"],
    url="http://pypi.python.org/pypi/markdown2Mathjax/",
    license="LICENSE.txt",
    description="Extend markdown2 for use with mathjax",
    long_description=open("README.txt").read(),
    install_requires=[
        "markdown2",
    ],
)
