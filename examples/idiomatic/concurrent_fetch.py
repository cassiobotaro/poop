"""
Concurrent Fetch

An `async def` in a class body is a method, and sending it answers a
coroutine: its body has not run yet. `x.await_()` runs it and answers its
value, and only an async method may send it. `Async.gather` awaits several
coroutines at once, so the three pages below take about as long as the
slowest one, not the sum of the three. `Async.run` starts it all from the
top of the program.

A block cannot await. It answers the coroutine instead, and the method
awaits what the block answered: `map` turns each url into a coroutine, and
`if_true_if_false` picks which one to await.

Smalltalk:
    | results semaphore |
    results := OrderedCollection new.
    semaphore := Semaphore new.
    urls do: [:url |
        [(Delay forMilliseconds: 30) wait.
         results add: url size.
         semaphore signal] fork].
    urls size timesRepeat: [semaphore wait].
"""


class Site(Object):
    def __init__(self, cached):
        self.cached = cached

    async def fetch(self, url, delay):
        Async.sleep(delay).await_()
        return url + " (" + url.len().repr() + " bytes)"

    async def from_cache(self, url):
        return url + " (cached)"

    async def page(self, url):
        return (
            self.cached.includes(url)
            .if_true_if_false(
                lambda: self.from_cache(url),
                lambda: self.fetch(url, 0.03),
            )
            .await_()
        )

    async def all(self, urls):
        return Async.gather(*urls.map(lambda url: self.page(url))).await_()


site = Site(["home"])
Async.run(site.all(["home", "about", "contact"])).do(lambda line: line.print())
