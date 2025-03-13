import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stackview",
    version="0.14.1",
    author="Robert Haase",
    author_email="robert.haase@uni-leipzig.de",
    description="Interactive image stack viewing in jupyter notebooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haesleinhuepf/stackview/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["numpy!=1.19.4", "ipycanvas", "ipywidgets", "scikit-image", "ipyevents", "toolz", "matplotlib", "ipykernel", "imageio", "ipympl", "wordcloud"],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
    ],
    entry_points={
        'bia_bob_plugins': [
            'stackview_plugins = stackview._bia_bob_plugins:list_bia_bob_plugins',
        ]
    }
)
