"""
Product Pipeline

Filters a catalog by availability and price, then formats each item.
Demonstrates chained filter / filter_false / map / do on a List of Tuples.

Smalltalk:
    products := #(
        #('Apple'    120 true)
        #('Laptop'  3500 true)
        #('Banana'   80 false)
        #('Headset'  450 true)
        #('Phone'   2200 true)
        #('Cable'    30 false)
    ).

    (products
        select:      [:p | p third]
        thenReject:  [:p | p second > 1000]
        thenCollect: [:p | p first , ' $' , p second printString])
    do: [:line | Transcript showCr: line].
"""


class ProductCatalog:
    def run(self):
        products = [
            ("Apple",   120, True),
            ("Laptop", 3500, True),
            ("Banana",   80, False),
            ("Headset", 450, True),
            ("Phone",  2200, True),
            ("Cable",    30, False),
        ]

        products.filter(lambda p: p.at(2)).filter_false(
            lambda p: p.at(1) > 1000
        ).map(
            lambda p: p.at(0) + " $" + p.at(1).repr()
        ).do(
            lambda line: line.print()
        )


ProductCatalog().run()
