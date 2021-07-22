from sgkit.io.vcf import vcf_to_zarr
from numcodecs import Blosc
import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    source_vcf = args[0]
    target = args[1]
    # compressor = Blosc(cname='zstd', clevel=5, shuffle=Blosc.AUTOSHUFFLE)
    vcf_to_zarr(source_vcf, target, fields=["INFO/*", "FORMAT/*"], chunk_length=65536, chunk_width=2000)
