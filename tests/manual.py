import sys
import time
from ncoreparser import Client, SearchParamWhere, SearchParamType, ParamSort, ParamSeq


def print_category(msg):
    print("")
    print("*{:133}*".format("-"*133))
    print("|{:^133}|".format(msg))
    print("*{:^80}*{:^30}*{:^10}*{:^10}*".format("-"*80, "-"*30, "-"*10, "-"*10))
    print("|{:^80}|{:^30}|{:^10}|{:^10}|".format("Title", "Type", "Size", "ID"))
    print("*{:^80}*{:^30}*{:^10}*{:^10}*".format("-"*80, "-"*30, "-"*10, "-"*10))


def pretty_print(torrent):
    print("|{:^80}|{:^30}|{:^10}|{:^10}|".format(torrent['title'],
                                                 torrent['type'],
                                                 str(torrent['size']),
                                                 str(torrent['id'])))
    print("*{:^80}*{:^30}*{:^10}*{:^10}*".format("-"*80, "-"*30, "-"*10, "-"*10))





if __name__ == "__main__":
    start = time.time()

    print("Login")
    client = Client()
    client.open(sys.argv[1], sys.argv[2])

    print_category("Most seeded torrents/category")
    for t_type in SearchParamType:
        torrent = client.search(pattern="", type=t_type, number=1,
                                sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]
        pretty_print(torrent)

    print("")
    print("Donwnload torrent")
    torrent = client.search(pattern="Forrest gump", type=SearchParamType.SD_HUN, number=1,
                            sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]

    client.download(torrent, "/tmp", override=True)

    print_category("List by rss")
    torrents = client.get_by_rss(sys.argv[3])
    for torrent in torrents:
        pretty_print(torrent)

    print_category("List by activity")
    torrents = client.get_by_activity()
    for torrent in torrents:
        pretty_print(torrent)


    print_category("List by recommended")
    torrents = client.get_recommended(type=SearchParamType.SD_HUN)
    for torrent in torrents:
        pretty_print(torrent)

    client.close()
    end = time.time()

    diff = end-start
    print("\nElapsed time: {} sec.".format(diff))
