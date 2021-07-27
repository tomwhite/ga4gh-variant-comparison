import allel
from numcodecs import Blosc
import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    source_vcf = args[0]
    target = args[1]
    compressor = Blosc(cname="zstd", clevel=5, shuffle=Blosc.AUTOSHUFFLE)
    allel.vcf_to_zarr(
        source_vcf, target, fields="*", chunk_width=2000, compressor=compressor
    )
