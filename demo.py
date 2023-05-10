from oaps import *
import shortuuid
import pandas as pd

EPSILON = 0.3


def create_pk():
    shortuuid.set_alphabet('123456789abcdefghijkmnopqrstuvwxyz')
    return shortuuid.uuid()[:5]


def print_res(res):
    if len(res) > 0:
        for s in res[0]:
            r = get_db().json().get(s, '$.sentence')
            print(s)
            print(r)


def quickDemo():
    index_document("24f2g4g2", "Pasta alla carbonara is a characteristic dish of Lazio and more particularly of Rome, prepared with popular ingredients and with an intense flavour. Spaghetti alla puttanesca is an Italian pasta dish invented in Naples in the mid-20th century and made typically with tomatoes, olive oil, olives, anchovies, chili peppers, capers, and garlic—with vermicelli or spaghetti pasta.")
    index_document("902j20rv", "This is a technical document, it describes the SID sound chip of the Commodore 64. This post is about 8 bits computers, such as Commodore 64, ZX Spectrum and other home computers")

    res = check_document("this post is about commodore", 0.3)
    print(res)

    res = check_document("Pasta alla carbonara is a characteristic dish of Lazio", 0.3)
    print(res)


def loadCSV():
    cnt = 0
    df = pd.read_csv("mortensi.csv", usecols = ['Content'])
    for index, row in df.iterrows():
        index_document(create_pk(), row.values[0])
        cnt = cnt + 1

    print("Indexed {} elements".format(cnt))


def testCSV():
    res = check_document("Pasta alla carbonara is a characteristic dish of Lazio and more particularly of Rome, prepared with popular ingredients and with an intense flavour. Spaghetti alla puttanesca is an Italian pasta dish invented in Naples in the mid-20th century and made typically with tomatoes, olive oil, olives, anchovies, chili peppers, capers, and garlic—with vermicelli or spaghetti pasta. We are a bunch of people convinced that you have to pass through difficult, or better, impossible challenges to see an idea reach the production stage and possibly provide benefits.", EPSILON)
    print_res(res)

    res = check_document("This is a technical document, it describes the SID sound chip of the Commodore 64. This post is about 8 bits computers, such as Commodore 64, ZX Spectrum and other home computers", EPSILON)
    print_res(res)


init()
loadCSV()
testCSV()
#quickDemo()


