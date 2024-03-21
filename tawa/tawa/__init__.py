import logging
import os
import pkg_resources


def pull_version_for_tawa() -> str:
    """Pull version from tawa package or pyproject file depending on install pattern.

    There are two cases that exist for usage patterns.

    1. The install is done through requirements files in the tawa dirs. The module
       is then accessed through addition to the path.
    2. The install is done through a pip install tawa in a repo that does not have
       standard path access to tawa pyproject file for version reading.

    In the above cases we handle the version respectively

    1. The pyproject file is accessed through standard pathing and the configparser module.
       This module sets up a reader for the file and we obtain the version through the
       parsed config object under the keys 'project''version'
    2. The tawa module is attempted to be imported, if successful the pkg_resources
       package is then used for pulling version.

    This allows pulling the version of the module in both the cases outlined above, therefore
    tawa-inner-cli experiences no pathing issues with version pulling.

    Returns:
        str: version of the tawa module from pyproject.toml raw file
    """
    # test if tawa is importable, if it is pull version from there
    try:
        version = pkg_resources.get_distribution("tawa").version
        logging.info("Found tawa package, using package for version")
        return version

    except pkg_resources.DistributionNotFound:
        logging.warning("No tawa import, assuming in tawa or client and can pull from config file path")

        import configparser

        config = configparser.ConfigParser()
        # in the tawa workdir
        tawa_pyproject_path = "tawa/pyproject.toml"
        if not os.path.exists(tawa_pyproject_path):
            # if file not found assume in client container based off tawa project image where tawa is installed
            # implies that tawa is installed at /opt/tawa as this is the pattern present in tawa project builds
            # defined in the tawa repo
            tawa_pyproject_path = "/opt/tawa/tawa/pyproject.toml"
        if not os.path.exists(tawa_pyproject_path):
            logging.warning("Can't find tawa pyproject file, file path non-standard")

        logging.info(f"Loading from config path {tawa_pyproject_path}")
        config.read(tawa_pyproject_path)
        return config["project"]["version"][1:-1]


__version__ = pull_version_for_tawa()
