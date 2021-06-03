# Genomic Prediction rrBLUP Pipeline
Table of Contents
=================
* [Description](#Description)
* [Installation](#Installation)
* [Requirements](#Requirements)
* [Tutorial](#Tutorial)
   * [Data Pre-processing](#Data-Pre-processing)
   * [Cross-validation](#Cross-validation)
   * [Build Training rrBLUP Model](#Build-Training-rrBLUP-Model)
   * [Feature Selection](#Feature-Selection)
   * [Final rrBLUP Model](#Final-rrBLUP-Model)
* [References](#References)

## Description

## Installation
Clone the repository onto your computer or remote host if working on an hpc cluster.
```
git clone https://github.com/peipeiwang6/Genomic_prediction_in_Switchgrass.git
```

## Requirements
* Python 3.6.4
* [rrBLUP v. 4.6.1](https://cran.r-project.org/web/packages/rrBLUP/index.html) and [data.table v. 1.13.2](https://cran.r-project.org/web/packages/data.table/index.html) R packages

To run python scripts on an hpc cluster you must load Python 3.6.4.
```shell
module purge
module load GCC/6.4.0-2.28  OpenMPI/2.1.2  Python/3.6.4 # change versions and dependencies accordingly
```
Alternatively, you can run commands on the command line within a conda environment.

To run R scripts on an hpc cluster you must load the appropriate R version with rrBLUP installed, or install rrBLUP into your remote directory.
```shell
module purge
module load GCC/8.3.0  OpenMPI/3.1.4  R/4.0.2 # change versions and dependencies accordingly
# initiate R
R
# once in R, run the line below
install.packages('rrBLUP')
```

## Tutorial
### Data Pre-processing
>Step 1. Extract the biallelic SNPs from your genotype matrix (GVCF) using VCFTools. 
- The VCFTools package version depends on which version you install onto your computer or if you are using a specific version in the remote host you are connected to.
```shell
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

### Cross-validation
>Step 9.

>Step 10. 
- Inputs in order: 
  - genotype matrix in csv format
  - phenotype matrix in csv format
  - selected features file in plain text format or 'all'
  - column name of target trait in the phenotype matrix or 'all' for multiple traits
  - fold number of the cross-validation scheme
  - number of repetitions for the cross-validation scheme
  - cross-validation file
  - name of output file

```shell
#
Rscript 09_rrBLUP_fread.r geno.csv pheno.csv all all 5 10 CVFs.csv exome_geno
# 
Rscript 09_rrBLUP.r PCA5_geno.csv pheno.csv all all 5 10 CVFs.csv exome_pca
```
- Outputs:
  - Coef_exome_geno_trait.csv , R2_results_exome_geno.csv
  - Coef_exome_pca_trait.csv, R2_results_exome_pca.csv

### Build Training rrBLUP Model
>Step 11. Assign which individuals in your phenotype matrix will be in the testing set.
- Inputs in order:
  - phenotype matrix
  - column name of target trait in the phenotype matrix
  - number of splits
```
# 1/6 of individuals in the test set
# 5/6 of individuals in the training set
python 10_holdout_test_stratified.py pheno_YPACETATE.csv YPACETATE 6
```
- Output:
  - Test.txt which contains the list of individuals in the testing set

>Step 12. Build the rrBLUP model using the training set
- Inputs for 11_split_geno_pheno_fread.r:
  - genotype matrix
  - phenotype matrix
  - test set file
```shell
# Split the genotype and phenotype matrices into training and testing sets
Rscript 11_split_geno_pheno_fread.r geno.csv pheno_YPACETATE.csv Test.txt
```
- Inputs for 07_make_CVs.py:
  - training phenotype matrix 
  - fold number of the cross-validation scheme
  - number of repetitions for the cross-validation scheme
```shell
# Generate the cross-validation scheme file using the phenotype training data
python 07_make_CVs.py -file pheno_training.csv -cv 5 -number 10
```
- Inputs for 09_rrBLUP_fread.r:
  - training genotype matrix in csv format
  - training phenotype matrix in csv format
  - selected features file in plain text format or 'all'
  - column name of target trait in the phenotype matrix or 'all' for multiple traits
  - fold number of the cross-validation scheme
  - number of repetitions for the cross-validation scheme
  - cross-validation file
  - name of output file
```shell
# Build the rrBLUP model using the genotype and phenotype training data
Rscript 09_rrBLUP_fread.r geno_training.csv pheno_training.csv all all 5 10 CVFs.csv exome_geno
```
- Output:
  - from 11_split_geno_pheno_fread.r: geno_training.csv, pheno_training.csv
  - from 07_make_CVs.py: CVFs.csv
  - from 09_rrBLUP_fread.r: Coef_exome_geno.csv, R2_results_exome_geno.csv

### Feature Selection
>Step 13. Generate files containing lists of markers with the highest absolute coefficients.
- Inputs in order:
  - coefficient file
  - number of markers to start with
  - number of markers to stop at
  - step size
```shell
python 12_select_markers_according_to_abs_coef.py -coef Coef_exome_geno.csv -start 250 -stop 5250 -step 250
```
- Output:
  - several Markers_top250.txt files

### Final rrBLUP Model
>Step 14. Apply the genomic prediction rrBLUP model to the testing set using the selected genetic markers or based on population structure within the cross-validation scheme.
- Inputs in order:
  - genotype matrix
  - phenotype matrix
  - selected features file in plain text format or 'all'
  - column name of target trait in the phenotype matrix or 'all' for multiple traits
  - test set file
  - fold number of the cross-validation scheme
  - number of repetitions for the cross-validation scheme
  - cross-validation file
  - name of output file
```shell
Rscript 13_rrBLUP_training_test_split.r geno.csv pheno.csv Markers_top250.txt target_trait Test.txt 5 10 CVFs.csv Markers_top250_geno
```
- Output:
  - Selected features' genotype information: geno_Markers_top250.txt.csv 
  - Cross-validation accuracy: R2_cv_results_Markers_top250_geno.csv, 
  - Testing set accuracy: R2_test_results_Markers_top250_geno.csv

To apply the genomic prediction model based on the population structure, use the top 5 principal components (PCs) for randomly selected markers.
- Inputs for 14_random_select_subset.r:
  - genotype matrix
  - number of markers to start with
  - number of markers to stop at
  - total number of markers in genotype matrix
```shell
# Select a random number of markers
Rscript 14_random_select_subset.r geno.csv start stop step total_number
```
- Inputs for 15_rrBLUP_pca_for_subset_markers.r:
  - random markers genotype matrix
  - phenotype matrix
  - selected features file in plain text format or 'all'
  - column name of target trait in the phenotype matrix or 'all' for multiple traits
  - test set file
  - fold number of the cross-validation scheme
  - number of repetitions for the cross-validation scheme
  - cross-validation file
  - name of output file
```shell
# apply the population structure
Rscript 15_rrBLUP_pca_for_subset_markers.r geno_250.csv pheno.csv selected_markers target_trait Test.txt 5 10 CVFs.csv Random_250_markers_pca
```
- Output:
  - from 14_random_select_subset.r: several geno_250.csv files containing n randomly selected markers
  - from 15_rrBLUP_pca_for_subset_markers.r: 
        - geno_selected_markers.csv
        - Coef_save_name.csv
        - R2_cv_results_Random_250_markers_pca.csv
        - R2_test_results_Random_250_markers_pca.csv

## References
Endelman, J.B. 2011. Ridge regression and other kernels for genomic selection with R package rrBLUP. Plant Genome 4:250-255.
