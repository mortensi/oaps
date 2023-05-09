from oaps import *

init()

index_document("24f2g4g2", "Pasta alla carbonara is a characteristic dish of Lazio and more particularly of Rome, prepared with popular ingredients and with an intense flavour. Spaghetti alla puttanesca is an Italian pasta dish invented in Naples in the mid-20th century and made typically with tomatoes, olive oil, olives, anchovies, chili peppers, capers, and garlic—with vermicelli or spaghetti pasta.")
index_document("902j20rv", "This is a technical document, it describes the SID sound chip of the Commodore 64. This post is about 8 bits computers, such as Commodore 64, ZX Spectrum and other home computers")

res = check_document("this post is about commodore", 0.3)
print(res)

res = check_document("Pasta alla carbonara is a characteristic dish of Lazio", 0.3)
print(res)