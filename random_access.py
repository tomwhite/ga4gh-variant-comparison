import sys

import numpy as np
import sgkit as sg

def export_region(path, region, sample_ids):
    ds = sg.load_dataset(path)

    variants_index = region_query(ds, region)
    samples_index = sample_ids_index(ds, sample_ids)

    # TODO: export as VCF
    print(ds.isel(variants=variants_index, samples=samples_index).load())


def export_slice(path, variant_slice, sample_ids):
    ds = sg.load_dataset(path)

    samples_index = sample_ids_index(ds, sample_ids)

    # TODO: export as VCF
    print(ds.isel(variants=variant_slice, samples=samples_index).load())


def region_query(ds, region):
    contig, start, end = parse_region(region)

    contig_index = ds.attrs["contigs"].index(contig)
    contig_range = np.searchsorted(ds.variant_contig.values, [contig_index, contig_index + 1])
    contig_pos = ds.variant_position.values[slice(contig_range[0], contig_range[1])]

    if start is None and end is None:
        variant_range = contig_pos
    elif end is None:
        # TODO: case where end is not specified
        pass
    else:
        variant_range = np.searchsorted(contig_pos, [start, end + 1]) + contig_range[0]
    
    return slice(variant_range[0], variant_range[1])


def parse_region(region):
    if ":" not in region:
        return region, None, None
    contig, start_end = region.split(":")
    start, end = start_end.split("-")
    start = int(start)
    end = int(end) if end != "" else None
    return contig, start, end


def sample_ids_index(ds, sample_ids):
    all_sample_ids = ds.sample_id.values
    all_sample_ids_index = np.argsort(all_sample_ids)
    all_sample_ids_sorted = all_sample_ids[all_sample_ids_index]
    sample_ids_sorted_index = np.searchsorted(all_sample_ids_sorted, sample_ids)
    sample_ids_index = np.take(all_sample_ids_index, sample_ids_sorted_index, mode="clip")
    return sample_ids_index


if __name__ == "__main__":
    args = sys.argv[1:]
    type = args[0]
    if type == "region":
        path, region, sample_ids  = args[1:]
        export_region(path, region, sample_ids.split(","))
    elif type == "slice":
        path, variant_slice, sample_ids  = args[1:]
        start, end = variant_slice.split(":")
        export_slice(path, slice(int(start), int(end)), sample_ids.split(","))
