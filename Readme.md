![Test](https://img.shields.io/github/actions/workflow/status/radaron/ncoreparser/module_test.yml?label=Test&style=for-the-badge)
[![pypi](https://img.shields.io/pypi/v/ncoreparser?style=for-the-badge)](https://pypi.org/project/ncoreparser/)
[![downloads](https://img.shields.io/pypi/dm/ncoreparser?style=for-the-badge)](https://pypi.org/project/ncoreparser/)
![license](https://img.shields.io/github/license/radaron/ncoreparser?style=for-the-badge)

# Ncoreparser

## Introduction

This module provides python API-s to manage torrents from ncore.pro eg.: search, download, rssfeed, etc..

## Install

``` bash
pip install ncoreparser
```

## Examples



### Search torrent
Get most seeded torrents from all category

``` python
from ncoreparser import Client, SearchParamWhere, SearchParamType, ParamSort, ParamSeq


if __name__ == "__main__":
    client = Client()
    client.login("<username>", "<password>")

    for t_type in SearchParamType:
        torrent = client.search(pattern="", type=t_type, number=1,
                                sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]
        print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

    client.logout()
```

### Download torrent
This example download Forest gump torrent file and save it to temp folder

``` python
from ncoreparser import Client, SearchParamWhere, SearchParamType, ParamSort, ParamSeq


if __name__ == "__main__":
    client = Client()
    client.login("<username>", "<password>")


    torrent = client.search(pattern="Forrest gump", type=SearchParamType.HD_HUN, number=1,
                            sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]

    client.download(torrent, "/tmp")
    client.logout()
```

### Download torrent by rssfeed
This example get all torrents and their informations from an ncore bookmark (rss feed)

``` python
from ncoreparser import Client


if __name__ == "__main__":
    client = Client()
    client.login("<username>", "<password>")

    torrents = client.get_by_rss("<rss url>")
    for torrent in torrents:
        print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

    client.logout()
```

### Get torrents by activity
This example get all torrents and their informations from the Hit&run page

``` python
from ncoreparser import Client


if __name__ == "__main__":
    client = Client()
    client.login("<username>", "<password>")

    torrents = client.get_by_activity()
    for torrent in torrents:
        print(torrent['title'], torrent['type'], torrent['size'],
              torrent['id'], torrent['rate'], torrent['remaining'])

    client.logout()
```

### Get recommended torrents
This example get all torrents and their informations from the recommended page

``` python
from ncoreparser import Client, SearchParamType


if __name__ == "__main__":
    client = Client()
    client.login("<username>", "<password>")

    torrents = client.get_recommended(type=SearchParamType.HD_HUN)
    for torrent in torrents:
        print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

    client.logout()
```

### Async support
The library also supports async calls. It works same as the sync version, but you have to use the AsyncClient class.

``` python
import asyncio
from ncoreparser import AsyncClient, SearchParamWhere, SearchParamType, ParamSort, ParamSeq


async def main():
    client = AsyncClient()
    await client.login("<username>", "<password>")

    for t_type in SearchParamType:
        torrent = await client.search(pattern="", type=t_type, number=1,
                                      sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]
        print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

    await client.logout()


if __name__ == "__main__":
    asyncio.run(main())
```