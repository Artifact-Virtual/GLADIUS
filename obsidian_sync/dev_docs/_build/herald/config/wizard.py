# Backup copy of wizard for archival consistency
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from copy import deepcopy
import textwrap

from herald.config.wizard import print_info


def print_legend():
    msg = "answer 'y' to start a new setup, or 'n' to use last saved"
    try:
        import shutil
        width = min(76, shutil.get_terminal_size().columns)
    except Exception:
        width = 76
    wrapped = textwrap.fill(msg, width=width)
    for ln in wrapped.splitlines():
        print_info(ln)

# The rest of the backup wizard is omitted in the backup file - this file exists to
# keep an archival copy of the helper in case restore is needed.
