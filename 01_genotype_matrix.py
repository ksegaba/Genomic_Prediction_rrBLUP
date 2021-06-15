#!/bin/python
"""
Author: Peipei Wang
Modified by: Kenia Segura Abá
"""
import sys,os,argparse

def warn(*args, **kwargs):
	pass
import warnings
warnings.warn = warn

def main():
	parser = argparse.ArgumentParser(description='This code is for converting the genotype gvcf to matrix format')
	# Required
	req_group = parser.add_argument_group(title='REQUIRED INPUT')
	req_group.add_argument('-file', help='genotype gvcf file', required=True)
	
	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(0)
	args = parser.parse_args()
	
	inp = open(args.file,'r')
	inl = inp.readline()
	D = {}
	out = open(args.file+'_genotype_matrix','w')
	while inl:
		if inl.startswith('#CHROM'):
			tem = inl.split('\t')[9:]
			out.write('Chr\tPos\tRef\tAlt\t%s'%'\t'.join(tem))
			out.flush()
		if not inl.startswith('#'):
			tem = inl.strip().split('\t')
			chr = tem[0]
			pos = tem[1]
			ref = tem[3]
			alt = tem[4].split(',')
			geno = tem[9:]
			res = '%s\t%s\t%s\t%s'%(chr,pos,ref,tem[4])
			for g in geno:
				type = g.split(':')[0]
				type = type.replace('0',ref)
				if '1' in type:
					type = type.replace('1',alt[0])
				if '2' in type:
					type = type.replace('2',alt[1])
				if '3' in type:
					type = type.replace('3',alt[2])
				if '4' in type:
					type = type.replace('4',alt[3])
				if '5' in type:
					type = type.replace('5',alt[4])
				if '6' in type:
					type = type.replace('6',alt[5])
				if '7' in type:
					type = type.replace('7',alt[6])
				res = res + '\t%s'%type	
			out.write(res + '\n')
			out.flush()
		inl = inp.readline()
	
	out.close()

if __name__ == '__main__':
	main()
