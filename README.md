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
>Step 1. Convert your Genomic VCF (GVCF) file to a genotype matrix in plain text format (TXT).
```bash
python 01_conver_genotype_gvcf_to_genotype_matrix.py -file your_gvcf.gvcf
```
output: your_gvcf.gvcf_genotype_matrix.txt

>Step 2. Filter

### Build rrBLUP model


### Troubleshooting

## References
Endelman, J.B. 2011. Ridge regression and other kernels for genomic selection with R package rrBLUP. Plant Genome 4:250-255.
