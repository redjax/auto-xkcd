# auto-xkcd

Query the [XKCD API](https://xkcd.com/json.html).

- [minio-py Github](https://github.com/minio/minio-py)
- [minio-py examples](https://github.com/minio/minio-py/tree/master/examples)
- [minio Python API client reference](https://min.io/docs/minio/linux/developers/python/API.html)

## Usage

### pdm scripts

```toml
[tool.pdm.scripts]

start-scrape = { cmd = "python src/auto_xkcd/cli.py pipelines scrape --overwrite-serial --loop-requests --max-loops 0 --loop-pause 3600", env = { "ENV_FOR_DYNACONF" = "prod" } }

start-scrape-dev = { cmd = "python src/auto_xkcd/cli.py pipelines scrape --overwrite-serial --loop-requests --max-loops 0 --loop-pause 3600", env = { "ENV_FOR_DYNACONF" = "dev" } }

get-current = { cmd = "python src/auto_xkcd/cli.py pipelines get-current", env = { "ENV_FOR_DYNACONF" = "prod" } }

get-current-dev = { cmd = "python src/auto_xkcd/cli.py pipelines get-current", env = { "ENV_FOR_DYNACONF" = "dev" } }

update-db = { cmd = "python src/auto_xkcd/cli.py pipelines update-db", env = { "ENV_FOR_DYNACONF" = "prod" } }

update-db-dev = { cmd = "python src/auto_xkcd/cli.py pipelines update-db", env = { "ENV_FOR_DYNACONF" = "dev" } }

loop-update-db = { cmd = "python src/auto_xkcd/cli.py pipelines update-db -c", env = { "ENV_FOR_DYNACONF" = "prod" } }

loop-update-db-dev = { cmd = "python src/auto_xkcd/cli.py pipelines update-db -c", env = { "ENV_FOR_DYNACONF" = "dev" } }

lint = { cmd = "ruff check ./ --config ruff.ci.toml --fix" }

docker-build-main = { shell = "docker build -t autoxkcd -f containers/auto-xkcd/Dockerfile ." }

docker-build-main-nocache = { shell = "docker build -t autoxkcd -f containers/auto-xkcd/Dockerfile . --no-cache" }

dockerctl = { shell = "python dockerctl.py" }
```

## Planned Features

- Validators
  - `validate_int_list(lst: list[int] = None)`
    - Validate a list of `int`s
      - Ensure `type(lst)` is `list`
      - Ensure each object in `lst[:]` is of type `int`
  - `validate_cache_transport(_transport: hishel.CacheTransport = None)`
    - Validate a `hishel.CacheTransport`
      - Ensure transport is of type `hishel.CacheTransport`
  - `validate_path(p: t.Union[str, Path] = None)`
    - Ensure an input path is a string or Path
    - Ensure paths with `"~"` call `Path(p).expanduser()`
    - Return a `Path` object

- "Low-level" requests
  - A method to build `httpx.Request` objects from inputs
  - A method to send `httpx.Request`s and return an `httpx.Response`
  - A method to extract an `httpx.Response`'s `.bytes` property
  - A method to decode content into a dict

- Serialization
  - Method to pack a `dict` with `msgpack` and save to an output file
  - Method to unpack a `msgpack` into a `dict` from an input file

- Track metadata
  - Current comic metadata
    - comic number
    - last updated (the last time a current comic was retrieved)
  - Track downloaded images
    - Method to loop over comig images directory & compile list of integers by looping over filenames, extracting the `Path().stem`, and converting to an `int`
    - Functionality to ignore specific comic numbers (i.e. `404`)

- Error handling
  - Handle `None`/empty lists
  - Handle non-200 HTTP responses
  - Handle missing `XKCDComic.img_url`
  - Handle missing `XKCDComic.link`

- Data utilities
  - DuckDB
    - Track downloaded comics & saved images with `.parquet` file(s), load into a DuckDB at program startup
    - Retrieve from memory when called as a context manager

- Automation
  - Loop-able check of current comic (with configurable check interval)
  - Retrieve missing comics
    - Check for any missing images, loop requests to retrieve
  - Synchronize data
    - Check for any downloaded images and metadata that still believes it's missing
  - Pipelines
    - Get current comic pipeline
      - Load from cache/serialized, if recent request exists
    - Scrape missing comics
      - Loop over list of missing comic numbers
      - Make request, serialize, download image, return `XKCDComic` object
    - Request multiple/batch
      - Iterate over a list of comic numbers
      - Make request, serialize, download image, add `XKCDComic` object to a list, then return the list
