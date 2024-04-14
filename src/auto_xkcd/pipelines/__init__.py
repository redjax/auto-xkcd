"""Pipelines join packages & modules into processing workflows, where a set of inputs control the operations the pipeline takes.

Pipeline examples:

* `pipeline_current_comic()`: A pipeline to request, process (serialize,
    update `current_comic.json` file, etc), and return the current XKCD comic.
* `pipeline_multiple_comics`: A pipeline to loop over a list of comic numbers & download/save each one.

"""
