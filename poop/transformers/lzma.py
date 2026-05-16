from poop.types.lzma import Lzma, LZMACompressor, LZMADecompressor, LZMAFile

NAMESPACE: dict[str, object] = {
    "lzma": Lzma,
    "LZMAFile": LZMAFile,
    "LZMACompressor": LZMACompressor,
    "LZMADecompressor": LZMADecompressor,
}
