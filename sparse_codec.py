from numcodecs.abc import Codec
from numcodecs.compat import ensure_ndarray, ndarray_copy, ensure_text
from numcodecs.registry import register_codec

import numpy as np
from scipy.sparse import coo_matrix

import zarr
from numcodecs import Blosc, Delta


class Sparse(Codec):

    codec_id = "sparse"

    def __init__(self):
        pass

    def encode(self, buf):

        arr = ensure_ndarray(buf)

        # ensure 2D # TODO: reverse in decode
        arr = arr.reshape((arr.shape[0], -1))

        # convert to sparse
        sarr = coo_matrix(arr)

        print(sarr.nnz)

        # extract sparse arrays
        M, N = sarr.shape
        data, row, col = sarr.data, sarr.row, sarr.col

        # ensure all are of type i2
        # TODO: should be u2 (max 65,535)
        # note that this is the smallest it can be, o/w chunks are too small
        # TODO: could pack data into smaller array, since it is i1 (or smaller)
        dtype = "i2"
        data = data.astype(dtype)
        row = row.astype(dtype)
        col = col.astype(dtype)

        # setup output
        enc = np.concatenate((np.array([sarr.nnz, M, N], dtype=dtype), data, row, col))

        return enc

    def decode(self, buf, out=None):

        enc = ensure_ndarray(buf)

        size = enc[0]
        M = enc[1]
        N = enc[2]
        data = enc[3 : size + 3]
        row = enc[size + 3 : 2 * size + 3]
        col = enc[2 * size + 3 :]

        sarr = coo_matrix((data, (row, col)), shape=(M, N))

        dec = sarr.todense()

        # handle destination
        return ndarray_copy(dec, out)


if __name__ == "__main__":

    register_codec(Sparse)

    # a = np.array([
    #     [0, 1, 0],
    #     [0, 0, 1],
    #     [0, 0, 0]
    # ], dtype="i1")
    # s = coo_matrix(a)

    # print(s)
    # print(s.dtype, s.nnz, s.size)

    # print(s.data, s.row, s.col)

    # enc = np.concatenate((np.array([s.nnz], dtype="i4"), s.data, s.row, s.col))
    # print(enc)

    # codec = Sparse()
    # enc = codec.encode(a)
    # print(enc)

    # dec = codec.decode(enc)
    # print(dec)

    arr = zarr.open("chr22_gt.vcfzarr/calldata/GT")

    print(arr.chunks)

    chunks = arr.chunks

    arr0 = arr[: chunks[0], : chunks[1], : chunks[2]]

    print("sparsity arr0", np.count_nonzero(arr0) / arr0.size)

    compressor = Blosc(cname="zstd", clevel=5, shuffle=Blosc.SHUFFLE)
    filters = [Sparse(), Delta("i2")]

    z = zarr.open(
        "chr22_gt_sparse.vcfzarr",
        mode="w",
        filters=filters,
        compressor=compressor,
        shape=chunks,
        chunks=chunks,
        dtype="i1",
    )

    z[:] = arr0
