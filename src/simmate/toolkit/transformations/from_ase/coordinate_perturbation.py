# -*- coding: utf-8 -*-

from ase.ga.standardmutations import RattleMutation
from ase.ga.utilities import closest_distances_generator
from pymatgen.io.ase import AseAtomsAdaptor

from simmate.toolkit import Composition, Structure
from simmate.toolkit.transformations.base import Transformation


class CoordinatePerturbation(Transformation):
    """
    This is a wrapper around the `RattleMutation` in ase.ga
    https://gitlab.com/ase/ase/-/blob/master/ase/ga/standardmutations.py
    """

    io_scale = "one_to_one"
    ninput = 1
    allow_parallel = False

    def __init__(
        self,
        composition: Composition,
        ratio_of_covalent_radii: float = 0.1,
    ):

        # the closest_distances_generator is exactly the same as an
        # element-dependent distance matrix expect ASE puts this in dictionary
        # form the function requires a list of element integers
        element_ints = [element.number for element in composition]
        # the default of the ratio of covalent radii (0.1) is based on the ASE
        # tutorial of this function
        self.element_distance_matrix = closest_distances_generator(
            element_ints, ratio_of_covalent_radii
        )

    def apply_transformation(self, structure: Structure) -> Structure:

        # first I need to convert the structures to an ASE atoms object
        structure_ase = AseAtomsAdaptor.get_atoms(structure)

        # now we can make the generator
        self.rattle = RattleMutation(
            blmin=self.element_distance_matrix,  # distance cutoff matrix
            n_top=int(
                structure.composition.num_atoms
            ),  # number of atoms to optimize. I set this to all,
            # rattle_strength=0.8, # strength of rattling
            # rattle_prop=0.4, # propobility that atom is rattled
            # test_dist_to_slab=True,
            # use_tags=False,
            # verbose=False,
            # rng=np.random
        )

        #!!! Their code suggests the use of .get_new_individual() but I think
        # .mutate() is what we'd like
        new_structure_ase = self.rattle.mutate(structure_ase)

        # if the mutation fails, None is return
        if not new_structure_ase:
            return False

        # if it was successful, we have a new Atoms object
        # now convert back to a pymatgen object
        new_structure = AseAtomsAdaptor.get_structure(new_structure_ase)

        return new_structure
