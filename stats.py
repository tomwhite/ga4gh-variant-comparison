from pathlib import Path
import humanize
import numpy as np
import zarr


def get_file_size(file):
    return file.stat().st_size


def get_dir_size(dir):
    return sum(f.stat().st_size for f in dir.glob("**/*") if f.is_file())


def du(file):
    if file.is_file():
        return get_file_size(file)
    return get_dir_size(file)


def sparsity(dir):
    arr = zarr.open(str(dir))
    return np.count_nonzero(arr[:]) / arr.size


def gnusize(nbytes, format="%.1f"):
    return humanize.naturalsize(nbytes, gnu=True, format=format)


def print_stats(files):
    bcf_size = du(Path(files["BCF"]))
    for name, file in files.items():
        size = du(Path(file))
        print(f"{name}: {gnusize(size)} ({size / bcf_size:.2f})")
    s = sparsity(Path(f"{files['VCF Zarr (scikit-allel)']}/calldata/GT")) * 100.0
    print(f"GT sparsity: {s:.2f}%")


if __name__ == "__main__":

    files = {
        "BCF": "1kg_gt.bcf",
        "VCF": "1kg_gt.vcf.bgz",
        "SAV": "1kg_gt.sav",
        "VCF Zarr (scikit-allel)": "1kg_gt.vcfzarr",
        "VCF Zarr (sgkit)": "1kg_gt.sgzarr",
    }

    print("1000 genomes subset")
    print_stats(files)
    print()

    files = {
        "BCF": "chr22_gt.bcf",
        "VCF": "chr22_gt.vcf.bgz",
        "SAV": "chr22_gt.sav",
        "VCF Zarr (scikit-allel)": "chr22_gt.vcfzarr",
        "VCF Zarr (sgkit)": "chr22_gt.sgzarr",
    }

    print("1000 genomes chr22, GT only")
    print_stats(files)
    print()

    files = {
        "BCF": "chr22.bcf",
        "VCF": "chr22.vcf.gz",
        "SAV": "chr22.sav",
        "VCF Zarr (scikit-allel)": "chr22.vcfzarr",
        "VCF Zarr (sgkit)": "chr22.sgzarr",
    }

    print("1000 genomes chr22, all fields")
    print_stats(files)
    print()
