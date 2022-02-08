# -*- coding: utf-8 -*-

"""
This module is for Simmate's test suite. You'll only use this if you are
contributing to the source code and making new tests.

Nearly all of Simmate's tests stem from toolkit objects, so this file loads sample
objects using the `toolkit.base_data_types` module. These Structures and 
Compositions can be used in any test.

Read more on pytest fixtures [here](https://docs.pytest.org/en/6.2.x/fixture.html).
This file helps share fixtures accross files as described 
[here](https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files).
"""


import os
import pytest

from simmate.toolkit import base_data_types


COMPOSITIONS_STRS = [
    "Fe1",
    "Si2",
    "C4",
    "Ti2O4",
    "Al4O6",
    "Si4N4O2",
    "Si4O8",
    "Sr4Si4N8",
    "Mg4Si4O12",
]


def get_structure_files():
    """
    Lists the full filename paths all of the files in the following directory:
       - toolkit/base_data_types/test/test_structures
    """
    # We want the full path of these filenames, so we that's why there are
    # extra os joins here.
    structure_dir = os.path.join(
        os.path.dirname(base_data_types.__file__),
        "test",
        "test_structures",
    )
    cif_filenames = [os.path.join(structure_dir, f) for f in os.listdir(structure_dir)]
    return cif_filenames


STRUCTURE_FILES = get_structure_files()


@pytest.fixture(scope="package", params=COMPOSITIONS_STRS)
def composition(request):
    """
    Gives a iteratible parameter of example compositions, where the compositions
    are given as ToolkitComposition objects.

    Use this fixture when you want to run a test on all of these compositions
    one at a time. For example, you would run a test like...

    ``` python
    # This function will be ran once for each composition
    def test_example(composition):

        # Do something with your composition.
        # We use a dummy example line here.
        assert composition
    ```
    """
    return base_data_types.Composition(request.param)


@pytest.fixture(scope="package")
def sample_compositions():
    """
    Gives a dictionary of example compositions to use, where the compositions
    are given as ToolkitComposition objects.

    Use this fixture when you want to a specific compositions within a test.
    For example, you would run a test like...

    ``` python
    def test_example(sample_compositions):

        # grab your desired composition
        composition = sample_compositions["Si2"]

        # now run any test you'd like with the object.
        # We use a dummy example line here.
        assert composition == Composition("Si2")
    ```
    """
    return {c: base_data_types.Composition(c) for c in COMPOSITIONS_STRS}


@pytest.fixture(scope="package", params=STRUCTURE_FILES)
def structure(request):
    """
    Gives a iteratible parameter of example structures, where the structures
    are given as ToolkitStructure objects.

    Use this fixture when you want to run a test on all of these structures
    one at a time. For example, you would run a test like...

    ``` python
    # This function will be ran once for each structure
    def test_example(structure):

        # Do something with your structure.
        # We use a dummy example line here.
        assert structure
    ```
    """
    return base_data_types.Structure.from_file(request.param)


@pytest.fixture(scope="package")
def sample_structures():
    """
    Gives a dictionary of example structures to use.

    All of these structures are loaded from files located in...
        simmate/toolkit/base_data_types/test/test_structures

    The structures are given as ToolkitStructure objects and the key are the
    filenames they came from (excluding filename extensions)

    Use this fixture when you want to a specific structures within a test.
    For example, you would run a test like...

    ``` python
    def test_example(sample_structures):

        # grab your desired composition
        composition = sample_structures["C_mp-48_primitive"]

        # now run any test you'd like with the object.
        # We use a dummy example line here.
        assert structure
    ```
    """

    # Now load all of the structures. This is a dictionary that where you
    # can access structures with keys like "SiO2_mp-7029_primitive"
    structures = {
        filename.split(os.path.sep)[-1].strip(
            ".cif"
        ): base_data_types.Structure.from_file(filename)
        for filename in STRUCTURE_FILES
    }

    return structures