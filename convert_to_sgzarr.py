from sgkit.io.vcf import vcf_to_zarr
from numcodecs import Blosc
import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    source_vcf = args[0]
    target = args[1]
    compressor = Blosc(cname="zstd", clevel=5, shuffle=Blosc.AUTOSHUFFLE)
    vcf_to_zarr(
        source_vcf,
        target,
        target_part_size=None,
        fields=["INFO/*", "FORMAT/*"],
        field_defs={
            "INFO/CIEND": {"dimension": "ci_dim"},
            "INFO/CIPOS": {"dimension": "ci_dim"},
            "INFO/MEINFO": {"dimension": "meinfo_dim"},
        },
        exclude_fields=["INFO/MC", "INFO/SVLEN", "INFO/VT"],  # Number defined as .
        chunk_length=65536,
        chunk_width=2000,
        compressor=compressor,
    )
