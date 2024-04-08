import typing as t
from itertools import chain


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
