from __future__ import annotations

from itertools import chain
import typing as t

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


def prepare_list_shards(
    original_list: list = [], shards: int = 1, shard_size_limit: int = 15
) -> list[list[t.Any]]:
    """Accept an input list. If size of list > set shard_size_limit, break into list of smaller lists.

    Params:
        original_list (list): A list with a lot of objects.
        shards (int) | default=1: The number of shards to create. This value is dynamic; as the function loops, more
            shards will be added as needed.
        shard_size_limit (int) | default=2000: The size limit for individual list shards as the original_list is broken into smaller lists.

    Returns:
        (list[list[Any]]): A list of smaller lists.

    """

    def create_list_shards(
        in_list=original_list, shards=shards, shard_size_limit=shard_size_limit
    ) -> list[t.Any] | list[list[t.Any]]:
        """Sub function that loops until all shards are individually smaller than shard_size_limit."""
        ## Number of items in original list
        list_len: int = len(in_list)
        ## Divide by number of shards to get individual shard size
        shard_size: int = int(list_len / shards)

        if shard_size > shard_size_limit:
            ## Individual shards still too large
            exceeds_by: int = shard_size - shard_size_limit
            print(
                f"Individual shard size [{shard_size}] exceed shard size limit of [{shard_size_limit}] by [{exceeds_by}]. Creating additional shard."
            )

            ## Add another shard, then loop
            shards += 1
            sharded_list: list = create_list_shards(
                in_list=in_list, shards=shards, shard_size_limit=shard_size_limit
            )
        else:
            ## Shard size limit satisfied, build new list of sub-lists (shards) & return
            sharded_list: list = [
                in_list[i : i + shard_size] for i in range(0, len(in_list), shard_size)
            ]

            print(
                f"Created [{len(sharded_list)}] shards. Individual shard size: [{len(sharded_list[0])}]"
            )

        return sharded_list

    if len(original_list) <= shard_size_limit:
        log.debug(
            f"List does not need paritioning. Size: [{len(original_list)}/{shard_size_limit}]"
        )

        return original_list

    list_of_shards: list[t.Any] | list[list[t.Any]] = create_list_shards()

    return list_of_shards
