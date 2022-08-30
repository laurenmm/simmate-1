# -*- coding: utf-8 -*-

"""
This module is experimental and subject to change.
"""

from pathlib import Path

from pymatgen.io.vasp.outputs import Vasprun

from simmate.database.base_data_types import (
    Calculation,
    Forces,
    Structure,
    Thermodynamics,
    table_column,
)


class DynamicsRun(Structure, Calculation):
    """
    Holds results from a dynamics simulations -- often referred to as a molecular
    dynamics run.

    In addition to the attributes listed, you can also access all ionic steps
    of the run via the `structures` attribute. This attribute gives a list of
    `DynamicsIonicSteps`.
    """

    class Meta:
        app_label = "workflows"

    api_filters = dict(
        temperature_start=["range"],
        temperature_end=["range"],
        time_step=["range"],
        nsteps=["range"],
    )

    temperature_start = table_column.IntegerField(blank=True, null=True)
    """
    The starting tempertature of the simulation in Kelvin.
    """

    temperature_end = table_column.IntegerField(blank=True, null=True)
    """
    The ending tempertature of the simulation in Kelvin.
    """

    time_step = table_column.FloatField(blank=True, null=True)
    """
    The time in picoseconds for each step in the simulation.
    """

    nsteps = table_column.IntegerField(blank=True, null=True)
    """
    The total number of steps in the simulation. Note, this is the maximum cutoff
    steps set. In some cases, there may be fewer steps when the simulation is 
    stopped early.
    """

    def update_from_vasp_run(
        self,
        vasprun: Vasprun,
        corrections: list[tuple[str]],
        directory: Path,
    ):
        """
        Given a Vasprun object from a finished dynamics run, this will update the
        DynamicsRun table entry and the corresponding DynamicsIonicStep entries.

        #### Parameters

        vasprun :
            The final Vasprun object from the dynamics run outputs.
        corrections :
            List of errors and corrections applied to during the relaxation.
        directory :
            name of the directory that relaxation was ran in. This is only used
            to reference the archive file if it's ever needed again.
        """

        # The data is actually easier to access as a dictionary and everything
        # we need is stored under the "output" key
        data = vasprun.as_dict()["output"]

        # The only other data we need to grab is the list of structures. We can
        # pull the structure for each ionic step from the vasprun class directly.
        structures = vasprun.structures

        # Now let's iterate through the ionic steps and save these to the database.
        for number, (structure, ionic_step) in enumerate(
            zip(structures, data["ionic_steps"])
        ):
            # first pull all the data together and save it to the database. We
            # are saving this to an DynamicsIonicStepStructure datatable. To access this
            # model, we look need to use "structures.model".
            structure = self.structures.model.from_toolkit(
                number=number,
                structure=structure,
                energy=ionic_step.get("e_wo_entrp", None),
                site_forces=ionic_step.get("forces", None),
                lattice_stress=ionic_step.get("stress", None),
                temperature=self._get_temperature_at_step(number),
                dynamics_run=self,  # this links the structure to this dynamics run
            )
            structure.save()

        # lastly, we also want to save the corrections made and directory it ran in
        self.corrections = corrections
        self.directory = directory

        # Now we have the relaxation data all loaded and can save it to the database
        self.save()

    def _get_temperature_at_step(self, step_number: int):
        return step_number * self._get_temperature_step_size() + self.temperature_start

    def _get_temperature_step_size(self):
        return (self.temperature_end - self.temperature_start) / self.nsteps


class DynamicsIonicStep(Structure, Thermodynamics, Forces):
    """
    Holds information for a single ionic step of a `DynamicsRun`.

    Each entry will map to a `DynamicsRun`, so you should typically access this
    data through that class. The exception to this is when you want all ionic
    steps accross many relaxations for a machine learning input.
    """

    class Meta:
        app_label = "workflows"

    base_info = (
        ["number"] + Structure.base_info + Thermodynamics.base_info + Forces.base_info
    )

    api_filters = dict(
        number=["range"],
        temperature=["range"],
    )

    number = table_column.IntegerField()
    """
    This is ionic step number for the given relaxation. This starts counting from 0.
    """

    temperature = table_column.FloatField(blank=True, null=True)
    """
    Expected temperature based on the temperature_start/end and nsteps. Note
    that in-practice some steps may not be at equilibrium temperatue. This could
    be the 1st 100 steps of a run or alternatively when the thermostat component
    is off-temperature.
    """

    # TODO: Additional options from Vasprun.as_dict to consider adding
    # e_0_energy
    # e_fr_energy
    # kinetic
    # lattice kinetic
    # nosekinetic
    # nosepot

    # All structures in this table come from dynamics run calculations, where
    # there can be many structures (one for each ionic step) linked to a
    # single run. This means the start structure, end structure, and
    # those structure in-between are stored together here.
    # Therefore, there's just a simple column stating which relaxation it
    # belongs to.
    dynamics_run = table_column.ForeignKey(
        DynamicsRun,
        on_delete=table_column.CASCADE,
        related_name="structures",
    )
