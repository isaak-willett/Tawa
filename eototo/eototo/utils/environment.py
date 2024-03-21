import os
from typing import Dict


def get_aws_creds() -> Dict[str, str]:
    """Get AWS creds from the host machine.

    These are used for accessing AWS with varying credential access
    patterns. The use case is that the container has been granted the
    current users access keys for read, write, etc... for reading data
    from cloud, writing data to cloud, starting cloud processes, etc...

    Generally these are used with something like Hashicorp Vault which
    allows the management of these secrets and temporary access. The
    dev machine or cloud instance (in some cases) are then granted
    the credentials to their dev machine before being loaded into
    the user created container session.

    This differs from roles based access pattern where this is not
    neccessary. In this case the credentials can either be turned off
    or have no affect if the role is properly set, access is granted
    through that SSO managed IAM role. These do not conflict and have
    no impact in said case.

    This is used for a multitude of uses cases in ADAS NA & JA where
    users access data.

    1. User local workflows
    2. CI Integration Tests
    3. CI Unit Tests Requiring Data Access
    4. Some Outlier Cloud Workflows

    Returns:
        Dict[str, str]: credentials for aws access taken from host ENV vars
    """
    return {
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", default=""),
        "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION", default=""),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", default=""),
        "AWS_SESSION_TOKEN": os.environ.get("AWS_SESSION_TOKEN", default=""),
    }


def get_artifactory_creds() -> Dict[str, str]:
    """Get Artifactory creds from the host machine.

    Returns multiple tokens in case access is handled differently.

    Returns:
        Dict[str, str]: credentials for Artifactory access taken from host ENV vars
    """
    return {
        "ARTIFACTORY_USER": os.environ.get("ARTIFACTORY_USER", default=""),
        "ARTIFACTORY_TOKEN": os.environ.get("ARTIFACTORY_TOKEN", default=""),
    }
