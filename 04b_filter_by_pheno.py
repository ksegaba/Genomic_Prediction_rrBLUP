'''
Author: Kenia Segura Abá
subset phenotype and genotype matrices to only include isolates/individuals with phenotype data
Input: The final genotype matrix (..._geno.csv) of diploid isolates only from running
python 06_convert_imputed_biallelic_variation_to_genotype.py 
-matrix 1011Matrix_genotype_matrix_filtered_biallelic_SNP_diploid.txt 
-imputed_matrix 1011Matrix_genotype_matrix_filtered_biallelic_SNP_diploid_Imputed.out_hapguess_switch.out

The output will be used in 08_getPCs.r
'''
import sys,os,argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='This code is for subsetting the genotype and phenotype matrices to only include individuals with phenotype data')
    # Required
    req_group = parser.add_argument_group(title='REQUIRED INPUT')
    req_group.add_argument('-p', help='phenotype matrix file', required=True)
    req_group.add_argument('-g', help='genotype matrix file', required=True)
    
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()

    inf = pd.read_csv(args.p) # ex. 'phenoMatrix_35ConditionsNormalizedByYPD.csv'
    geno = pd.read_csv(args.g) # ex. '1011Matrix_genotype_matrix_filtered_biallelic_SNP_diploid.txt_imputed_geno.csv'
    print("pheno", inf.shape, "\ngeno", geno.shape)

    # reset index of pheno matrix to isolate names & transpose the data
    inf.set_index(inf.iloc[:,0]) # inf = inf.set_index("Unnamed: 0")
    tinf = inf.transpose() # transpose of inf
    print("pheno transpose", tinf.shape)

    # filter the phenotype matrix to extract only diploid isolates
    tinf_diploid = tinf[tinf.columns.intersection(geno.ID)]
    print("pheno transpose, only diploid", tinf_diploid.shape)

    # filter the genotype matrix to extract only isolates with pheno info
    geno = geno.set_index("ID")
    tgeno = geno.transpose()
    print("geno transpose", tgeno.shape)
    geno2 = tgeno[tgeno.columns.intersection(tinf_diploid.columns)]
    print("geno transpose, only diploid", geno2.shape)
    geno = geno2.transpose()
    print("geno final matrix, only diploid", geno.shape)
    pheno = tinf_diploid.transpose()
    print("pheno final matrix, only diploid", pheno.shape)

    # reset indeces
    geno = geno.reset_index()
    pheno = pheno.reset_index()

    # save new geno and pheno matrices to output files
    pheno.to_csv('pheno.csv', header=True, index=False)
    geno.to_csv('geno.csv', header=True, index=False)

if __name__ == '__main__':
	main()