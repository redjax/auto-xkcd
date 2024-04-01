from __future__ import annotations

from pathlib import Path
import time
import typing as t

from core import COMIC_IMG_DIR, request_client
import hishel
import httpx
from loguru import logger as log
from modules import xkcd_mod
from packages import xkcd
import pandas as pd
from pipelines import helpers
from red_utils.std import hash_utils


def save_img_update_csv(
    comic_res: httpx.Response = None,
    comic: xkcd_mod.XKCDComic = None,
    output_dir: t.Union[str, Path] = COMIC_IMG_DIR,
):
    assert comic_res, ValueError("Missing httpx.Response object")
    assert isinstance(comic_res, httpx.Response), TypeError(
        f"Expected comic_res to be of type httpx.Response. Got type: ({type(comic_res)})"
    )

    assert comic, ValueError("Missing xkcd_mod.XKCDComic object")
    assert isinstance(comic, xkcd_mod.XKCDComic), TypeError(
        f"comic must be of type xkcd_mox.XKCDComic. Got type: ({type(comic)})"
    )

    assert output_dir, ValueError("Missing image file output directory")
    assert isinstance(output_dir, str) or isinstance(output_dir, Path), TypeError(
        f"output_dir must be a str or Path. Got type: ({type(output_dir)})"
    )
    if isinstance(output_dir, Path):
        if "~" in f"{output_dir}":
            output_dir: Path = output_dir.expanduser()
    elif isinstance(output_dir, str):
        if "~" in output_dir:
            output_dir: Path = Path(output_dir).expanduser()
        else:
            output_dir: Path = Path(output_dir)

    filename: str = f"{comic.comic_num}.png"

    if Path(f"{output_dir}/{filename}").exists():
        log.warning(
            f"Image file already exists at '{output_dir}/{filename}'. Skipping save & updating CSV file."
        )

        with xkcd.helpers.ComicNumsController() as comic_nums:
            data = xkcd_mod.ComicNumCSVData(comic_num=comic.comic_num, img_saved=True)
            try:
                comic_nums.add_comic_num_data(data.model_dump())
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception updating existing comic image's data in CSV file. Details: {exc}"
                )
                log.error(msg)
    else:
        log.debug(f"Saving image to path '{output_dir}/{filename}")
        try:
            xkcd.save_img(
                comic=comic_res,
                output_dir=output_dir,
                output_filename=filename,
            )

            try:
                with xkcd.helpers.ComicNumsController() as comic_nums:
                    data = xkcd_mod.ComicNumCSVData(
                        comic_num=comic.comic_num, img_saved=True
                    )

                    comic_nums.add_comic_num_data(data.model_dump())
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception updating CSV file. Details: {exc}"
                )
                log.error(msg)

        except Exception as exc:
            msg = Exception(f"Unhandled exception saving image. Details: {exc}")
            log.error(msg)

            raise msg


def pipeline_current_comic(
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
    save_serial: bool = True,
    save_to_db: bool = False,
) -> xkcd_mod.XKCDComic:
    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT

    try:
        current_comic_res: httpx.Response = xkcd.request_current_comic()
        url_hash: str = xkcd.helpers.url_hash(url=current_comic_res.url)
        log.debug(f"URL hash: {url_hash}")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current XKCD comic. Details: {exc}"
        )

        raise msg

    log.info(">> Start current comic pipeline")

    try:
        current_comic_dict: dict = xkcd.helpers.parse_comic_response(
            res=current_comic_res
        )
        comic_hash: str = xkcd.helpers.comic_num_hash(
            comic_num=current_comic_dict["num"]
        )
        log.debug(f"Comic num [{current_comic_dict['num']}] hash: {comic_hash}")

        ## Append hashes to response dict
        current_comic_dict["url_hash"] = url_hash

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    current_comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic().model_validate(
        current_comic_dict
    )
    ## Set current_comic.link to xkcd homepage (link for current comic is always null)
    current_comic.link = "https://xkcd.com"
    # log.info(f"Current comic: {current_comic}")

    if save_serial:
        serial_filename: str = str(current_comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            xkcd.helpers.serialize_response(
                res=current_comic_res, filename=serial_filename
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    if save_to_db:
        log.warning(
            f"save_to_db=True, but method is not yet implemented. Skipping save to database."
        )
        pass

    try:
        save_img_update_csv(comic_res=current_comic_res, comic=current_comic)
        log.success(f"Image for comic #{current_comic.comic_num} saved.")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving comic #{current_comic.comic_num} image. Details: {exc}"
        )
        log.error(msg)

        with xkcd.helpers.ComicNumsController() as comic_nums:
            data = xkcd_mod.ComicNumCSVData(
                comic_num=current_comic.comic_num, img_saved=False
            )

            comic_nums.add_comic_num_data(data.model_dump())

    log.info("<< End current comic pipeline")

    return current_comic


def pipeline_random_comic(
    save_serial: bool = True,
    save_to_db: bool = False,
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
) -> xkcd_mod.XKCDComic:
    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT

    random_comic_res: httpx.Response = xkcd.get_random_comic(transport=transport)
    # log.debug(f"Random comic response: {random_comic_res}")

    random_comic_dict = xkcd.helpers.parse_comic_response(res=random_comic_res)

    log.info(">> Start random comic pipeline")

    try:
        comic_hash: str = xkcd.helpers.comic_num_hash(
            comic_num=random_comic_dict["num"]
        )
        log.debug(f"Comic num [{random_comic_dict['num']}] hash: {comic_hash}")

        ## Append hashes to response dict
        random_comic_dict["url_hash"] = xkcd.helpers.url_hash(url=random_comic_res.url)

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    random_comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic().model_validate(
        random_comic_dict
    )
    # log.debug(f"Random comic: {random_comic}")

    if save_serial:
        serial_filename: str = str(random_comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            xkcd.helpers.serialize_response(
                res=random_comic_res, filename=serial_filename
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    if save_to_db:
        log.warning(
            f"save_to_db=True, but method is not yet implemented. Skipping save to database."
        )
        pass

    try:
        save_img_update_csv(comic_res=random_comic_res, comic=random_comic)
        log.success(f"Image for comic #{random_comic.comic_num} saved.")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving comic #{random_comic.comic_num} image. Details: {exc}"
        )
        log.error(msg)

        with xkcd.helpers.ComicNumsController() as comic_nums:
            data = xkcd_mod.ComicNumCSVData(
                comic_num=random_comic.comic_num, img_saved=False
            )

            comic_nums.add_comic_num_data(data.model_dump())

    log.info("<< End random comic pipeline")

    return random_comic


def pipeline_specific_comic(
    comic_num: t.Union[str, int] = None,
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
    save_serial: bool = True,
    save_to_db: bool = False,
) -> xkcd_mod.XKCDComic:
    assert comic_num, ValueError("Missing comic number for pipeline")
    assert isinstance(comic_num, str) or isinstance(comic_num, int), TypeError(
        f"comic_num should be a string or integer. Got type: ({type(comic_num)})"
    )

    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT

    log.info(">> Start specific comic pipeline")

    try:
        comic_res: httpx.Response = xkcd.get_comic(
            comic_num=comic_num, transport=transport
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)

        raise msg

    try:
        comic_dict: dict = xkcd.helpers.parse_comic_response(res=comic_res)
        comic_num_hash: str = xkcd.helpers.comic_num_hash(comic_num=comic_dict["num"])
        log.debug(f"Comic num [{comic_dict['num']}] hash: {comic_num_hash}")

        ## Append hashes to response dict
        comic_dict["url_hash"] = hash_utils.get_hash_from_str(input_str=comic_res.url)
        log.debug(f"URL hash: {comic_dict['url_hash']}")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(comic_dict)

    if save_serial:
        serial_filename: str = str(comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            xkcd.helpers.serialize_response(res=comic_res, filename=serial_filename)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    if save_to_db:
        log.warning(
            f"save_to_db=True, but method is not yet implemented. Skipping save to database."
        )
        pass

    try:
        save_img_update_csv(comic_res=comic_res, comic=comic)
        log.success(f"Image for comic #{comic.comic_num} saved.")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving comic #{comic.comic_num} image. Details: {exc}"
        )
        log.error(msg)

        with xkcd.helpers.ComicNumsController() as comic_nums:
            data = xkcd_mod.ComicNumCSVData(comic_num=comic.comic_num, img_saved=False)

            comic_nums.add_comic_num_data(data.model_dump())

    log.info("<< End specific comic pipeline")

    return comic


def pipeline_multiple_comics(
    comic_nums_list: list[int] = None,
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
    save_serial: bool = True,
    save_to_db: bool = False,
    request_sleep: int = 5,
) -> list[xkcd_mod.XKCDComic]:
    assert comic_nums_list, ValueError("Missing list of comic_nums to request")
    assert isinstance(comic_nums_list, list), TypeError(
        f"comic_nums_list must be a list of ints. Got type: ({type(comic_nums_list)})"
    )
    for i in comic_nums_list:
        assert isinstance(i, str) or isinstance(i, int), TypeError(
            f"Each value in comic_nums_list must be an integer or string. Got type: ({type(i)}) for value '{i}'."
        )

    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT

    log.info(">> Start multi-comic pipeline")

    multiple_comics_res: list[httpx.Response] = xkcd.get_multiple_comics(
        comic_nums_list=comic_nums_list
    )

    multiple_comic_dicts: list[dict] = []
    multiple_comics: list[xkcd_mod.XKCDComic] = []

    for r in multiple_comics_res:
        if r.status_code == 404:
            log.warning(
                f"404 unfound response: [{r.status_code}: {r.reason_phrase}]: {r.text}"
            )
            continue

        p: dict = xkcd.helpers.parse_comic_response(res=r)
        multiple_comic_dicts.append(p)

        c: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(p)
        multiple_comics.append(c)

        try:
            save_img_update_csv(comic_res=r, comic=c)
            log.success(f"Image for comic #{c.comic_num} saved.")
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception saving comic #{c.comic_num} image. Details: {exc}"
            )
            log.error(msg)

            with xkcd.helpers.ComicNumsController() as comic_nums:
                data = xkcd_mod.ComicNumCSVData(comic_num=c.comic_num, img_saved=False)

                comic_nums.add_comic_num_data(data.model_dump())

                if c.comic_num not in comic_nums.as_list():
                    helpers.time.pause(
                        duration=request_sleep,
                        pause_msg=f"Sleeping for {request_sleep} second(s)...",
                    )

    if save_serial:
        for c in multiple_comics:
            serial_filename: str = str(c.comic_num) + ".msgpack"

            try:
                log.debug(f"Serialized filename: {serial_filename}")
                xkcd.helpers.serialize_response(res=r, filename=serial_filename)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception serializing comic response. Details: {exc}"
                )
                log.error(msg)

    if save_to_db:
        log.warning(
            f"save_to_db=True, but method is not yet implemented. Skipping save to database."
        )
        pass

    log.info("<< End multi-comic pipeline")

    return multiple_comics


def pipeline_retrieve_missing_imgs(
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
    save_serial: bool = True,
    save_to_db: bool = False,
    request_sleep: int = 5,
):
    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT

    log.info(">> Start retrieve missing comic imgs pipeline")

    with xkcd.helpers.ComicNumsController() as cnums_controller:
        try:
            missing_df: pd.DataFrame = cnums_controller.df.loc[
                cnums_controller.df["img_saved"] == False
            ]
            log.debug(f"Downloading [{missing_df.shape[0]}] missing image(s)")
        except KeyError as key_err:
            msg = Exception(
                f"Could not find image by comic number. Is the DataFrame empty?"
            )
            log.warning(msg)

            return

        missing_comic_nums: list[int] = missing_df["comic_num"].to_list()
        if missing_comic_nums:
            log.debug(
                f"Missing comic nums [{len(missing_comic_nums)}]: {missing_comic_nums}"
            )

    for comic_num in missing_comic_nums:
        try:
            missing_comic_res: httpx.Response = xkcd.get_comic(comic_num=comic_num)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting missing comic #{comic_num} data."
            )
            log.error(msg)

        try:
            missing_comic_dict: dict = xkcd.helpers.parse_comic_response(
                res=missing_comic_res
            )
            missing_comic_num_hash: str = xkcd.helpers.comic_num_hash(
                comic_num=missing_comic_dict["num"]
            )
            log.debug(
                f"Missing comic num [{missing_comic_dict['num']}] hash: {missing_comic_num_hash}"
            )

            ## Append hashes to response dict
            missing_comic_dict["url_hash"] = hash_utils.get_hash_from_str(
                input_str=missing_comic_res.url
            )
            log.debug(f"URL hash: {missing_comic_dict['url_hash']}")

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception parsing missing XKCD comic response. Details: {exc}"
            )
            log.error(msg)

            raise msg

        comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(
            missing_comic_dict
        )

        if save_serial:
            serial_filename: str = str(missing_comic_dict["num"]) + ".msgpack"

            try:
                log.debug(f"Serialized filename: {serial_filename}")
                xkcd.helpers.serialize_response(
                    res=missing_comic_res, filename=serial_filename
                )
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception serializing missing comic response. Details: {exc}"
                )
                log.error(msg)

        if save_to_db:
            log.warning(
                f"save_to_db=True, but method is not yet implemented. Skipping save to database."
            )
            pass

        try:
            save_img_update_csv(comic_res=missing_comic_res, comic=comic)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception saving missing image for comic #{comic.comic_num}. Details: {exc}"
            )
            log.error(msg)

            with xkcd.helpers.ComicNumsController() as comic_nums:
                data = xkcd_mod.ComicNumCSVData(
                    comic_num=comic.comic_num, img_saved=False
                )

                comic_nums.add_comic_num_data(data.model_dump())

                if comic.comic_num not in comic_nums.as_list():
                    helpers.time.pause(
                        duration=request_sleep,
                        pause_msg=f"Sleeping for {request_sleep} second(s)...",
                    )

        helpers.time.pause(
            duration=request_sleep,
            pause_msg=f"Sleeping for {request_sleep} second(s)...",
        )

    log.info("<< End retrieve missing comic imgs pipeline")


def pipeline_update_img_saved_vals(imgs_dir: Path = COMIC_IMG_DIR) -> None:
    """Iterate over all requested comics & saved images, set `True` values for images downloaded."""
    log.info(">> Start update 'img_saved' CSV value pipeline")
    try:
        xkcd.helpers.update_comic_num_img_bool(img_dir=imgs_dir)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception running pipeline to update 'img_saved' value in CSV file. Details: {exc}"
        )
        log.error(msg)

        raise msg

    log.info("<< End update 'img_saved' CSV value pipeline")
