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
# Peipei Wang's repository
git clone https://github.com/peipeiwang6/Genomic_prediction_in_Switchgrass.git

# To download additional scripts not in Peipei's repository
git clone https://github.com/ksegaba/Genomic_Prediction_rrBLUP.git
```

## Requirements
* Python 3.6.4
* [rrBLUP v. 4.6.1](https://cran.r-project.org/web/packages/rrBLUP/index.html) and [data.table v. 1.13.2](https://cran.r-project.org/web/packages/data.table/index.html) R packages
* [fastPHASE](http://scheet.org/software.html)

To run python scripts on an hpc cluster you must load Python 3.6.4.
```shell
module purge
module load GCC/6.4.0-2.28  OpenMPI/2.1.2  Python/3.6.4 # change versions and dependencies accordingly
```
Alternatively, you can run commands on the command line. If you have issues with importing python libraries, run them within a conda environment.

To run R scripts on an hpc cluster you must load the appropriate R version with rrBLUP installed, or install rrBLUP into your remote directory.
```shell
module purge
module load GCC/8.3.0  OpenMPI/3.1.4  R/4.0.2 # change versions and dependencies accordingly
# initiate R
R
# once in R, run the line below
install.packages('rrBLUP')
```

Download and install fastPHASE software for imputation of missing genotypes.
```shell
curl -O http://scheet.org/code/Linuxfp.tar.gz # Download Linux executable
gunzip Linuxfp.tar.gz
tar -xvf Linuxfp.tar
chmod a+x fastPHASE # change permissions to allow all users to run fastPHASE
```

## Tutorial
### Data Pre-processing
>Step 1. Convert GVCF to a matrix format.
```shell
python 01_genotype_matrix.py -file your_gvcf.gvcf
```
- Output:
   - your_gvcf_genotype_matrix  

>Step 2. Filter your genotype matrix by minor allele frequency (MAF > 0.05).
```shell
python 02_filter_genotype_matrix_MAF_missing_data.py -file your_gvcf_genotype_matrix
```
- Output:
   - your_gvcf_genotype_matrix_filtered 

>Step 3. Filter your genotype matrix to extract biallelic SNPs.
```shell
python 03_get_biallelic_markers_directly.py -file your_gvcf_genotype_matrix_filtered -type SNP
```
- Output:
   - your_gvcf_genotype_matrix_filtered_biallelic_SNP.txt  

>Step 4. Filter your genotype matrix to extract diploid individuals.
- Inputs in order:
   - genotype matrix from step 3
   - tsv or txt file containing information on ploidy of individuals (column 1 is individuals, column 2 is ploidy)
          -   ploidy needs to be coded in numbers (*i.e.* 2 for diploid)
```shell
python 04_filter_diploid.py -file your_gvcf_genotype_matrix_filtered_biallelic_SNP.txt -labels labels.tsv
```
- Output:
   - your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid.txt  
    
>Step 5. Convert your genotype matrix into fastPHASE format.
```shell
python 05_convert_genotype_matrix_to_fastPHASE_format.py -file your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid.txt 
```
- Output:
   - your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid.txt_fastPHASE.txt

>Step 6. Impute missing data using fastPHASE.
```shell
./fastPHASE -T10 -o your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid_Imputed.out 1011Matrix_genotype_matrix_filtered_biallelic_SNP_diploid.txt_fastPHASE.txt
```
- Output:
   - your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid_Imputed.out
   - your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid_Imputed.out_hapguess_switch.out
   - your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid_Imputed.out_origchars

>Step 7. Convert the imputed genotype matrix (in fastPHASE format) back to the format used previously.
```shell
python 06_convert_imputed_biallelic_variation_to_genotype.py -matrix your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid.txt -imputed_matrix your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid_Imputed.out_hapguess_switch.out
```
- Output:
   - your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid.txt_imputed_geno.csv
   - your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid.txt_imputed.txt

### Cross-validation (CV)
>Step 8. Make the cross-validation file for the 5-fold CV scheme repeated 10 times
```shell
# filter your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid.txt_imputed_geno.csv to only include individuals with phenotype data
python 04b_filter_by_pheno.py -p pheno.csv -g your_gvcf_genotype_matrix_filtered_biallelic_SNP_diploid.txt_imputed_geno.csv

# make CV file
python 07_make_CVs.py -file pheno.csv -cv 5 -number 10
```
- Output: 
   - from 04b_filter_by_pheno.py: pheno.csv, geno.csv
   - from 07_make_CVs.py: CVFs.csv

>Step 9. Estimate the population structure as the top 5 principal components based on the genetic markers.
- Inputs in order: 
   - genotype matrix in csv format
   - phenotype matrix in csv format 
```shell
Rscript 08_getPCs.r geno.csv pheno.csv
```
- Output:
   - EVD.RData
   - PCA_matrix.csv
   - PCA5_geno.csv
   - VarExplained.pdf
   - diag.pdf
   - PCs.pdf
   - VarExplained.csv

>Step 10. Build rrBLUP CV model using genetic markers and population structure. 
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
# build rrBLUP model based on genetic markers
Rscript 09_rrBLUP_fread.r geno.csv pheno.csv all all 5 10 CVFs.csv exome_geno

# build rrBLUP model based on population structure
Rscript 09_rrBLUP.r PCA5_geno.csv pheno.csv all all 5 10 CVFs.csv exome_pca
```
- Outputs:
  - Coef_exome_geno_trait.csv , R2_results_exome_geno.csv
  - Coef_exome_pca_trait.csv, R2_results_exome_pca.csv
The Coef files contain coefficient estimates for the effects of individual genetic markers or principal components on the phenotype value. The R2 results files contain estimates for the R-squared, which was calculated using the true and predicted values of the phenotype for all the individuals in the population, for each repetition of the CV scheme.

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
# Build rrBLUP model using the training genotype and phenotype data.
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
python 12_select_markers_according_to_abs_coef.py -coef Coef_exome_geno.csv -start 250 -stop 5250 -step 250 # change accordingly
```
- Output:
  - several Markers_top....txt files

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

__Important Note:__ The cross-validation file (CVFs.csv) must be built based on the training data (pheno_training.csv). If you use pheno.csv, your R-squared results may return NAs.
```shell
# build the rrBLUP models using selected markers from Markers_top....txt files for feature selection
Rscript 13_rrBLUP_training_test_split.r geno.csv pheno.csv Markers_top250.txt target_trait Test.txt 5 10 CVFs.csv Markers_top250_geno

# build the baseline rrBLUP model using all genetic markers
Rscript 13_rrBLUP_training_test_split.r geno.csv pheno.csv all target_Trait Test.txt 5 10 CVFs.csv exome_geno
```
- Output:
  - Selected features' genotype information: geno_Markers_top250.txt.csv
  - Cross-validation scheme rrBLUP accuracy: R2_cv_results_Markers_top250_geno.csv, R2_cv_results_exome_geno.csv
  - Testing set accuracy: R2_test_results_Markers_top250_geno.csv, R2_test_results_exome_geno.csv

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
  - from 14_random_select_subset.r: several geno_n.csv files containing n randomly selected markers (250, 500, etc.)
  - from 15_rrBLUP_pca_for_subset_markers.r: 
        - geno_selected_markers.csv
        - Coef_save_name.csv
        - R2_cv_results_Random_250_markers_pca.csv
        - R2_test_results_Random_250_markers_pca.csv

## References
Endelman, J.B. 2011. Ridge regression and other kernels for genomic selection with R package rrBLUP. Plant Genome 4:250-255.

Scheet P, Stephens M (2006). A Fast and Flexible Statistical Model for Large-Scale Population Genotype Data: Applications to Inferring Missing Genotypes and Haplotypic Phase. American Journal of Human Genetics 78:629–644
