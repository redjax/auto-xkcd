import typing as t
from itertools import chain

from loguru import logger as log


def join_list_of_lists(list_of_lists: list[list[t.Any]] = None) -> list[t.Any]:
    """Join a list of other lists into a single list."""
    assert list_of_lists, ValueError("Missing list of lists to join")
    assert isinstance(list_of_lists, list), TypeError(
        f"list_of_lists must be a list of other lists. Got type: ({type(list_of_lists)})"
    )
    for lst in list_of_lists:
        assert isinstance(lst, list), TypeError(
            f"All lists within list_of_lists must be of type list. Got type: ({type(lst)})"
        )

    ## Concatenate all lists into one using chain, then convert to set to remove duplicates
    unique_elements = set(chain(*list_of_lists))

    ## Convert set back to list
    joined_list: list[t.Any] = list(sorted(unique_elements))
    return joined_list


def make_list_chunks(
    input_list: list[t.Any] = None, max_list_size: int = 50
) -> list[list[t.Any]] | list[t.Any]:
    """Break a list into smaller lists/"chunks" based on max_list_size.

    Params:
        input_list (list): The input list to be chunked.
        max_list_size (int): The maximum size of each chunk.

    Returns:
        list of lists: List of smaller lists or chunks.

    """
    assert input_list, ValueError("Missing input list to break into smaller chunks")
    assert isinstance(input_list, list), TypeError(
        f"input_list must be a list. Got type: ({type(input_list)})"
    )

    if max_list_size == 0 or max_list_size is None:
        log.warning(
            f"No limit set on list size. Returning full list embedded in another list"
        )

        return input_list

    chunked_list: list[list] = []
    ## Loop over objects in list, breaking into smaller list chunks each time
    #  the iterator reaches max_list_size
    for i in range(0, len(input_list), max_list_size):
        chunked_list.append(input_list[i : i + max_list_size])

    log.debug(
        f"Created [{len(chunked_list)}] list(s) of {max_list_size} or less items."
    )

    return chunked_list
