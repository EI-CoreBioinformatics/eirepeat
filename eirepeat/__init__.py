import pkg_resources

__title__ = "eirepeat"
__author__ = "Gemy Kaithakottil (kaithakg)"
__email__ = "Gemy.Kaithakottil@earlham.ac.uk"
__copyright__ = "Copyright 2019-2022 Earlham Institute"
__version__ = pkg_resources.require("eirepeat")[0].version


DEFAULT_PAP_CONFIG_FILE = pkg_resources.resource_filename(
    "eirepeat.etc", "eirepeat_config.yaml"
)
DEFAULT_PAP_RUN_CONFIG_FILE = pkg_resources.resource_filename(
    "eirepeat.etc", "run_config.yaml"
)
DEFAULT_HPC_CONFIG_FILE = pkg_resources.resource_filename(
    "eirepeat.etc", "hpc_config.json"
)
FULL_SPECIES_TREE_FILE = pkg_resources.resource_filename(
    "eirepeat.etc", "queryRepeatDatabase.tree.txt"
)
