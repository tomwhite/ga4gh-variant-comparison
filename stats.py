from pathlib import Path
import numpy as np
import zarr

def get_file_size(file):
    return file.stat().st_size

def get_dir_size(dir):
    return sum(f.stat().st_size for f in dir.glob('**/*') if f.is_file())

def sparsity(dir):
    arr = zarr.open(str(dir))
    return np.count_nonzero(arr[:]) / arr.size

if __name__ == "__main__":
    bcf_size = get_file_size(Path("1kg_gt.bcf"))
    sav_size = get_file_size(Path("1kg_gt.sav"))
    vcf_size = get_file_size(Path("1kg_gt.vcf.bgz"))
    vcfzarr_size = get_dir_size(Path("1kg_gt.vcfzarr"))
    sgzarr_size = get_dir_size(Path("1kg_gt.sgzarr"))

    bcf_size = get_file_size(Path("chr22_gt.bcf"))
    sav_size = get_file_size(Path("chr22_gt.sav"))
    vcf_size = get_file_size(Path("chr22_gt.vcf.bgz"))
    vcfzarr_size = get_dir_size(Path("chr22_gt.vcfzarr"))
    sgzarr_size = get_dir_size(Path("chr22_gt.sgzarr"))

    # bcf_size = get_file_size(Path("chr22.bcf"))
    # sav_size = get_file_size(Path("chr22.sav"))
    # vcf_size = get_file_size(Path("chr22.vcf.gz"))
    # vcfzarr_size = get_dir_size(Path("chr22.vcfzarr"))

    print(f"BCF: {bcf_size} (1.00)")
    print(f"SAV: {sav_size} ({sav_size / bcf_size:.2f})")
    print(f"VCF: {vcf_size} ({vcf_size / bcf_size:.2f})")
    print(f"VCF Zarr (scikit-allel): {vcfzarr_size} ({vcfzarr_size / bcf_size:.2f})")
    print(f"VCF Zarr (sgkit): {sgzarr_size} ({sgzarr_size / bcf_size:.2f})")
    s = sparsity(Path("chr22_gt.vcfzarr/calldata/GT")) * 100.0
    print(f"GT sparsity: {s:.2f}%")
