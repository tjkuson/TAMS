"""
Common file operation methods.
"""

import logging
import os
import shutil
from pathlib import Path

from tqdm import tqdm

from client.dialogues.progress import ProgressDialogue


def create_dir_if_missing(path: Path) -> None:
    """Create a directory if one does not exist.

    :param path: target directory
    """
    if not path.exists():
        os.makedirs(path, exist_ok=True)
        logging.info("Created directory at %s.", path)


def move_or_copy_item(
    item: Path, destination_directory: Path, keep_original: bool = True
) -> None:
    """Function that copies or moves item to a given location.

    :param item: target item
    :param destination_directory: destination location
    :param keep_original: determines if move or copy
    """

    if keep_original:
        verb = "Copying"
    else:
        verb = "Moving"

    logging.info(
        "%s %s to %s...",
        verb,
        item,
        destination_directory,
    )

    create_dir_if_missing(destination_directory)

    try:

        # Check file or directory is a file or directory, respectively
        if item.is_file():
            shutil.copy(item, destination_directory / item.name)
        elif item.is_dir():
            shutil.copytree(item, destination_directory / item.name)

        # Delete original if not keeping original
        if not keep_original:
            if item.is_file():
                os.remove(item)
            elif item.is_dir():
                os.rmdir(item)

    # If source and destination are same
    except shutil.SameFileError:
        logging.exception("Exception raised.")
    # If any permission issue
    except PermissionError:
        logging.exception("Exception raised.")
    except FileExistsError:
        # Just move on if the file already exists
        logging.info(
            "File already exists at %s, skipping", destination_directory / item.name
        )


def find_and_move(
    glob_arg: str,
    search_dir: Path,
    *destinations: Path,
    copy: bool = False,
    gui: bool = False,
) -> None:
    """Function that finds files using .glob method in given directory and moves them to
    another directory.

    :param copy: doesn't delete original if true
    :param glob_arg: argument passed to .glob method
    :param search_dir: directory that is searched
    :param destinations: list of destinations
    """

    number_of_counters = len(list(search_dir.glob(glob_arg)))
    if number_of_counters:
        for destination in destinations:
            if gui:
                progress_dialogue = ProgressDialogue(
                    len(list(search_dir.glob(glob_arg)))
                )
            for item in list(search_dir.glob(glob_arg)):
                # Copy file to local reconstructed data directory
                move_or_copy_item(
                    item,
                    Path(search_dir) / Path(destination),
                )
                if gui:
                    progress_dialogue.add_progress(1)
        for item in tqdm(
            search_dir.glob(glob_arg),
            f"Deleting {glob_arg} files from {search_dir}",
            total=len(list(search_dir.glob(glob_arg))),
        ):
            if not copy:
                if item.is_file():
                    os.remove(item)
                elif item.is_dir():
                    shutil.rmtree(item)
    else:
        logging.warning("No %s files found.", glob_arg)