"""Methods & pipelines for interacting with the [XKCD API](https://www.xkcd.com/info.0.json).

Handles requesting the current XKCD comic on an interval, caching HTTP requests & serializing the responses,
and creating Pydantic schemas & SQLAlchemy database models for each comic.

Images are saved as bytestrings to .png files (and eventually withing a database or .parquet file).
"""
