.. image:: https://github.com/radaron/ncoreparser-python/workflows/Python%20application/badge.svg


***********
Ncoreparser
***********

Introduction
############

This module provides python API-s to manage torrents from ncore.cc eg.: search, download, rssfeed, etc..


Install
#######

.. code-block:: bash

   pip install ncoreparser

Examples
########


**Search torrent**
Get most seeded torrents from all category

.. code-block:: python

    from ncoreparser import Client, SearchParamWhere, SearchParamType, ParamSort, ParamSeq


    if __name__ == "__main__":
        client = Client()
        client.open("<username>", "<password>")

        for t_type in SearchParamType:
            torrent = client.search(pattern="", type=t_type, number=1,
                                    sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]
            print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

        client.close()

**Download torrent**
This example download Forest gump torrent file and save it to temp folder

.. code-block:: python

    from ncoreparser import Client, SearchParamWhere, SearchParamType, ParamSort, ParamSeq


    if __name__ == "__main__":
        client = Client()
        client.open("<username>", "<password>")


        torrent = client.search(pattern="Forrest gump", type=SearchParamType.SD_HUN, number=1,
                                sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]

        client.download(torrent, "/tmp")
        client.close()

**Download torrent by rssfeed**
This example get all torrents and their informations from an ncore bookmark (rss feed)

.. code-block:: python

    from ncoreparser import Client


    if __name__ == "__main__":
        client = Client()
        client.open("<username>", "<password>")

        torrents = client.get_by_rss("<rss url>")
        for torrent in torrents:
            print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

        client.close()

**Get torrents by activity**
This example get all torrents and their informations from the Hit&run page

.. code-block:: python

    from ncoreparser import Client

    if __name__ == "__main__":
        client = Client()
        client.open("<username>", "<password>")

        torrents = client.get_by_activity()
        for torrent in torrents:
            print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

        client.close()

**Get recommended torrents**
This example get all torrents and their informations from the recommended page

.. code-block:: python

    from ncoreparser import Client, SearchParamType

    if __name__ == "__main__":
        client = Client()
        client.open("<username>", "<password>")

        torrents = client.get_recommended(type=SearchParamType.SD_HUN)
        for torrent in torrents:
            print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

        client.close()
