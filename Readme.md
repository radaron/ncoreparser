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
    cookies = client.login("<username>", "<password>")

    for t_type in SearchParamType:
        torrent = client.search(
            pattern="",
            type=t_type,
            sort_by=ParamSort.SEEDERS,
            sort_order=ParamSeq.DECREASING
        ).torrents[0]
        print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

    client.logout()
```

### Cookie persistence
Save and reuse cookies to avoid re-authentication (if cookies haven't expired):

``` python
import json
import os
from ncoreparser import Client

COOKIE_FILE = "ncore_cookies.json"

saved_cookies = None
if os.path.exists(COOKIE_FILE):
    with open(COOKIE_FILE, 'r') as f:
        saved_cookies = json.load(f)

client = Client(cookies=saved_cookies)

if not client._logged_in:
    cookies = client.login("<username>", "<password>")
    with open(COOKIE_FILE, 'w') as f:
        json.dump(cookies, f)

torrents = client.get_by_activity()
```

### Download torrent
This example download Forest gump torrent file and save it to temp folder

``` python
from ncoreparser import Client, SearchParamWhere, SearchParamType, ParamSort, ParamSeq


if __name__ == "__main__":
    client = Client()
    cookies = client.login("<username>", "<password>")


    torrent = client.search(
        pattern="Forrest gump",
        type=SearchParamType.HD_HUN,
        sort_by=ParamSort.SEEDERS,
        sort_order=ParamSeq.DECREASING
    ).torrents[0]

    client.download(torrent, "/tmp")
    client.logout()
```

### Download torrent by rssfeed
This example get all torrents and their informations from an ncore bookmark (rss feed)

``` python
from ncoreparser import Client


if __name__ == "__main__":
    client = Client()
    cookies = client.login("<username>", "<password>")

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
    cookies = client.login("<username>", "<password>")

    torrents = client.get_by_activity()
    for torrent in torrents:
        print(
            torrent['title'],
            torrent['type'],
            torrent['size'],
            torrent['id'],
            torrent['rate'],
            torrent['remaining']
        )

    client.logout()
```

### Get recommended torrents
This example get all torrents and their informations from the recommended page

``` python
from ncoreparser import Client, SearchParamType


if __name__ == "__main__":
    client = Client()
    cookies = client.login("<username>", "<password>")

    torrents = client.get_recommended(type=SearchParamType.HD_HUN)
    for torrent in torrents:
        print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

    client.logout()
```

### Two-factor authentication (2FA)
If your account has 2FA enabled, provide the code as the third parameter:

``` python
from ncoreparser import Client

client = Client()
cookies = client.login("<username>", "<password>", twofactorcode="123456")
```

### Async support
The library also supports async calls. It works same as the sync version, but you have to use the AsyncClient class.

``` python
import asyncio
from ncoreparser import AsyncClient, SearchParamWhere, SearchParamType, ParamSort, ParamSeq


async def main():
    client = AsyncClient()
    cookies = await client.login("<username>", "<password>")

    for t_type in SearchParamType:
        torrent = await client.search(
            pattern="",
            type=t_type,
            sort_by=ParamSort.SEEDERS,
            sort_order=ParamSeq.DECREASING
        ).torrents[0]
        print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

    await client.logout()


if __name__ == "__main__":
    asyncio.run(main())
```

**Note:** For async clients, cookies can be passed to `__init__()` but validation happens on the first async operation since `await` cannot be called in `__init__()`.