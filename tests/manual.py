import time
import argparse
from ncoreparser import Client, SearchParamType, ParamSort, ParamSeq


def print_category(msg):
    print("")
    print("*{:175}*".format("-" * 175))
    print(f"|{msg:^175}|")
    print(
        "*{:^100}*{:^30}*{:^10}*{:^10}*{:^10}*{:^10}*".format(
            "-" * 100, "-" * 30, "-" * 10, "-" * 10, "-" * 10, "-" * 10
        )
    )
    print("|{:^100}|{:^30}|{:^10}|{:^10}|{:^10}|{:^10}|".format("Title", "Type", "Size", "ID", "Seed", "Leech"))
    print(
        "*{:^100}*{:^30}*{:^10}*{:^10}*{:^10}*{:^10}*".format(
            "-" * 100, "-" * 30, "-" * 10, "-" * 10, "-" * 10, "-" * 10
        )
    )


def pretty_print(torrent):
    print(
        "|{:^100}|{:^30}|{:^10}|{:^10}|{:^10}|{:^10}|".format(
            torrent["title"],
            torrent["type"],
            str(torrent["size"]),
            str(torrent["id"]),
            torrent["seed"],
            torrent["leech"],
        )
    )
    print(
        "*{:^100}*{:^30}*{:^10}*{:^10}*{:^10}*{:^10}*".format(
            "-" * 100, "-" * 30, "-" * 10, "-" * 10, "-" * 10, "-" * 10
        )
    )


parser = argparse.ArgumentParser()
parser.add_argument("--user", "-u", required=True, type=str)
parser.add_argument("--passw", "-p", required=True, type=str)
parser.add_argument("--rss-feed", "-r", required=True, type=str)

args = parser.parse_args()


if __name__ == "__main__":
    start = time.time()

    print("Login")
    client = Client(timeout=5)
    client.login(args.user, args.passw)

    print_category("Most seeded torrents/category")
    for t_type in SearchParamType:
        result = client.search(pattern="", type=t_type, sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)
        pretty_print(result.torrents[0])

    print_category("Donwnload torrent")
    result = client.search(
        pattern="Forrest",
        type=SearchParamType.HD_HUN,
        sort_by=ParamSort.SEEDERS,
        sort_order=ParamSeq.DECREASING,
    )
    pretty_print(result.torrents[0])
    client.download(result.torrents[0], "/tmp", override=True)

    print_category("List by rss")
    torrents = client.get_by_rss(args.rss_feed)
    for torrent in torrents:
        pretty_print(torrent)

    print_category("List by activity")
    torrents = client.get_by_activity()
    for torrent in torrents:
        pretty_print(torrent)

    print_category("List by recommended")
    torrents = client.get_recommended(type=SearchParamType.HDSER_HUN)
    for torrent in torrents:
        pretty_print(torrent)

    client.logout()
    end = time.time()

    diff = end - start
    print(f"\nElapsed time: {diff} sec.")
