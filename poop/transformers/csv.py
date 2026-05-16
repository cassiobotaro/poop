from poop.types.csv import CSV, DictReader, DictWriter, Reader, Sniffer, Writer

NAMESPACE: dict[str, object] = {
    "csv": CSV,
    "Reader": Reader,
    "Writer": Writer,
    "DictReader": DictReader,
    "DictWriter": DictWriter,
    "Sniffer": Sniffer,
}
