# Genomic Prediction rrBLUP Pipeline
Table of Contents
=================
* [Description](#Description)
* [Installation](#Installation)
* [Requirements](#Requirements)
* [Tutorial](#Tutorial)
   * [Data Pre-processing](#Data-Pre-processing)
   * [Build rrBLUP model](#Build-rrBLUP-model)
   * [Troubleshooting](#Troubleshooting)
* [References](#References)

## Description

## Installation
Clone the repository onto your computer.
```
git clone https://github.com/peipeiwang6/Genomic_prediction_in_Switchgrass.git
```

## Requirements
* Python 3.6.4
* [rrBLUP v. 4.6.1](https://cran.r-project.org/web/packages/rrBLUP/index.html) and [data.table v. 1.13.2](https://cran.r-project.org/web/packages/data.table/index.html) R packages

## Tutorial
### Data Pre-processing
>Step 1. Extract the biallelic SNPs from your genotype matrix (GVCF) using VCFTools. 
- The VCFTools package version depends on which version you install onto your computer or if you are using a specific version in the remote host you are connected to.
```
# In the remote host
module purge # unload all loaded modules
module load GNU/7.3.0-2.30  OpenMPI/3.1.1-CUDA  VCFtools/0.1.15-Perl-5.28.0 # change versions accordingly
vcftools --vcf your_gvcf.gvcf --min-alleles 2 --max-alleles 2 --recode --out your_gvcf_biallelic
```
- Output: 
    - your_gvcf_biallelic.recode.vcf
    - your_gvcf_biallelic.log

>Step 2. Filter biallelic SNPs by minor allele frequency
```

```

>Step 1. Convert your Genomic VCF (GVCF) file to a genotype matrix in plain text format (TXT).
```bash
python 01_conver_genotype_gvcf_to_genotype_matrix.py -file your_gvcf.gvcf
```
output: your_gvcf.gvcf_genotype_matrix.txt



### Build rrBLUP model


### Troubleshooting

## References
Endelman, J.B. 2011. Ridge regression and other kernels for genomic selection with R package rrBLUP. Plant Genome 4:250-255.
