# GA4GH Future of VCF comparison

Experiments for scaling VCF.

Questions:
* How do the various formats (BCF, SAV, VCF Zarr) compare for compressed size?
    * For all fields?
    * For just GT?
* How fast is it to compress each format?
    * Is sgkit faster than scikit-allele?
* How fast is it to decompress each format?
* What effect does phasing have?

Refs:
* Genotype compressor benchmark http://alimanfoo.github.io/2016/09/21/genotype-compression-benchmark.html

## Comparison of BCF, SAV, VCF Zarr

For 1000 genomes chr22 (GT only)
```
BCF: 128.6M (1.00)
SAV: 53.4M (0.42)
VCF: 156.1M (1.21)
VCF Zarr (scikit-allel): 56.5M (0.44)
VCF Zarr (sgkit): 56.5M (0.44)
GT sparsity: 3.71%
```

For 1000 genomes chr22 (all fields)
```
BCF: 163.3M (1.00)
SAV: 66.9M (0.41)
VCF: 196.1M (1.20)
VCF Zarr (scikit-allel): 74.7M (0.46)
VCF Zarr (sgkit): 74.4M (0.46)
GT sparsity: 3.71%
```

To generate SAV from BCF took only 30s, but 5m27 from bgzip compressed VCF.
To generate VCF Zarr it took 5m17 from bgzip compressed VCF - so very comparable.
So it looks like parsing VCF dominates.

## Sparse codec

Question: does using a Zarr filter that takes advantage of sparseness help?

Answer: not much (for size at least)

```bash
python sparse_codec.py 
ls -l chr22_gt_sparse.vcfzarr/0.0.0 # 2270380
ls -l chr22_gt.vcfzarr/calldata/GT/0.0.0 # 2741718
```

0.828 - a 13% saving - so not *that* significant.
We could do a better job of packing bits though.

## How to run

Generate input files

Download chr22 from http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ 

```bash
cp ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz chr22.vcf.gz
cp ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz.tbi chr22.vcf.gz.tbi
~/sw/bcftools-1.10.2/bin/bcftools view -O b -o chr22.bcf ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz

# remove all INFO and FORMAT fields except GT
~/sw/bcftools-1.10.2/bin/bcftools annotate -x INFO,FORMAT -O b -o 1kg_gt.bcf 1kg.vcf.bgz
~/sw/bcftools-1.10.2/bin/bcftools annotate -x INFO,FORMAT -O z -o 1kg_gt.vcf.bgz 1kg.vcf.bgz

~/sw/bcftools-1.10.2/bin/bcftools annotate -x INFO,FORMAT -O b -o chr22_gt.bcf ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz
~/sw/bcftools-1.10.2/bin/bcftools annotate -x INFO,FORMAT -O z -o chr22_gt.vcf.bgz ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz
~/sw/htslib-1.10.2/bin/tabix chr22_gt.vcf.bgz
```

Convert to SAV

```bash
cget/bin/sav import -5 --phasing none 1kg_gt.bcf 1kg_gt.sav
cget/bin/sav import -5 --phasing none chr22_gt.bcf chr22_gt.sav
cget/bin/sav import -5 --phasing none chr22.bcf chr22.sav
```

Convert to VCF Zarr (scikit-allel)

```
python convert_to_vcfzarr.py 1kg_gt.vcf.bgz 1kg_gt.vcfzarr
python convert_to_vcfzarr.py chr22_gt.vcf.bgz chr22_gt.vcfzarr
python convert_to_vcfzarr.py chr22.vcf.gz chr22.vcfzarr
```

Convert to VCF Zarr (sgkit)

```
python convert_to_sgzarr.py 1kg_gt.vcf.bgz 1kg_gt.sgzarr
python convert_to_sgzarr.py chr22_gt.vcf.bgz chr22_gt.sgzarr
python convert_to_sgzarr.py chr22.vcf.gz chr22.sgzarr
```

## Random access

Region
```
cget/bin/sav export --regions "2:22665048-22780029" --sample-ids "HG02010,NA19764" 1kg_gt.sav out.vcf
python random_access.py region 1kg_gt.sgzarr "2:22665048-22780029" "HG02010,NA19764"
```

Slice
```
cget/bin/sav export --slice "1000:1002" --sample-ids "HG02010,NA19764" 1kg_gt.sav out.vcf
python random_access.py slice 1kg_gt.sgzarr "1000:1002" "HG02010,NA19764"
```

