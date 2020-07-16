#! /usr/bin/env python3
# coding: utf-8
import argparse
from subprocess import Popen, PIPE

def read_fasta(list_uniprot):
	res = {}
	list_inconnus = []
	l = list(range(1,23)) + ['x','y']
	for i in l:
		res[i] = []
	for gene in list_uniprot:
		trouv = False
		for numb in l:
			cmd = ["grep", "-c", gene, "Data/Human_by_chromosome/chromosome_"+str(numb)+".fasta"]
			p = Popen(cmd, stdout=PIPE, stderr=PIPE)
			stdout, stderr = p.communicate()
			if "1" in str(stdout):
				res[numb].append(gene)
				trouv = True
				break
		if not trouv:
			list_inconnus.append(gene)
	#print(list_inconnus)
	return res

		

def extract_composites(path): # Return type : {composite_gene_ID : [[(family,ID of the hit), ...], ...]} and each sub-list is a domain
	res = {}
	with open(path, "r") as composites_file:
		temp= {}
		name = ''
		domain_list = []
		family = []
		for line in composites_file:
			if line.startswith(">"):
				if name != '':
					domain_list.append(family)
					res[name] = domain_list
					temp= {}
					name = ''
					domain_list = []
					family = []
				name = line.strip()[1:]
			elif line.startswith("["):
				if family != []:
					domain_list.append(family)
					family = []
			elif line.startswith("F"):
				liste = line.split()
				family.append((liste[0], liste[1]))
	
	domain_list.append(family)
	res[name] = domain_list
	return res
	
	

def extract_dictionary(path):
	res = {}
	with open(path, "r") as dico_file:
		for line in dico_file:
			assoc = line.split()
			res[assoc[1]] = assoc[0]
	return res

def list_of_uniprot_composites(dico_composites, dico_names):
	if dico_composites == {'': [[]]}:
		return []
	res = []
	for ID in dico_composites.keys():
		res.append(dico_names[ID[1:]])
	return res 




def list_for_all_chromosomes(): # one list with all the composites genes
	res = []
	compt = 0
	l = list(range(1,23)) + ['x','y']
	for i in l:
		name = "chromosome_" + str(i)
		path_com ="Result/Human_by_chromosome/" + name + "_cleanNetwork_composites/" + name + "_cleanNetwork.composites"  
		dico_composites = extract_composites(path_com)
		#print(dico_composites)
		path_dico = "Result/Human_by_chromosome/" +name+ "_cleanNetwork_composites/" + name + ".cleanNetwork.dico" 
		dico_names = extract_dictionary(path_dico)
		temps = list_of_uniprot_composites(dico_composites, dico_names)
		compt += len(temps)
		res = res + temps
	return res


def list_by_chromosomes(): # a list of list of composite genes for each chromosomes.
	res = []
	compt = 0
	l = list(range(1,23)) + ['x','y']
	for i in l:
		name = "chromosome_" + str(i)
		path_com ="Result/Human_by_chromosome/" + name + "_cleanNetwork_composites/" + name + "_cleanNetwork.composites"  
		dico_composites = extract_composites(path_com)
		
		path_dico = "Result/Human_by_chromosome/" +name+ "_cleanNetwork_composites/" + name + ".cleanNetwork.dico" 
		dico_names = extract_dictionary(path_dico)
		temps = list_of_uniprot_composites(dico_composites, dico_names)
		compt += len(temps)
		res.append(temps)
	return res

def nb_components(list_of_uniprot_ID, dico_composites, inv_dico_names): # return the list of components of the target composites genes, in the all_vs_all computation
	res = []
	for ID in list_of_uniprot_ID:
		name = "C" + inv_dico_names[ID]
		l = dico_composites[name]
		for domain in l:
			#print('\nla', domain)
			for comp in domain:
				res.append(comp[1])	
	return len(res), len(set(res))


def composites_families(list_of_uniprot_ID, inv_dico_names):
	path = "Result/human_reviewed_cleanNetwork_composites/human_reviewed_cleanNetwork.compositesinfo"  
	list_names = [inv_dico_names[c] for c in list_of_uniprot_ID] 
	res = []
	with open(path, 'r') as families:
		for line in families:
			if not line.startswith('#'):
				infos = line.split()
				if infos[0][1:] in list_names:
					res.append(infos[2])
	return len(set(res))



def main():
	one_by_one = list_for_all_chromosomes()
	by_chromosome = list_by_chromosomes()
	
	path_com ="Result/human_reviewed_cleanNetwork_composites/human_reviewed_cleanNetwork.composites"  
	dico_composites = extract_composites(path_com)
	
	path_dico = "Result/human_reviewed_cleanNetwork_composites/human_reviewed.cleanNetwork.dico"
	dico_names = extract_dictionary(path_dico)
	
	all_vs_all = list_of_uniprot_composites(dico_composites, dico_names)
	#print(len(one_by_one), len(all_vs_all))
	intersect = [c for c in one_by_one if c in all_vs_all]
	inv_dico_names = {v:k for k,v in dico_names.items()}
	list_nb_genes = [1975 , 1249 , 1032 , 730 , 842 , 970 , 927 , 643 , 741 , 708 , 1258 , 986 , 310 , 698 , 559 , 794 , 1121 , 264 , 1372 , 525 , 221 , 464 , 790 , 37]
	dico_comp_by_genes = read_fasta(all_vs_all)
	
	result_file = "Docs/tableau_all_vs_all.md"
	with open(result_file, "w") as res:
		res.write("| Chromosome | Genes | Composites | Composites also found with one by one | Components (uniques) | Families of composites |\n")
		res.write("|------------|:-----:|:----------:|:--------------------:|:--------------------:|:----------------------:|\n")
		l = list(range(24))
		for i in l:
			if i+1 == 23:
				name = "chromosome_" + "x"
				numb = "x"
			elif i+1 == 24 :
				name = "chromosome_" + "y"
				numb = "y"
			else :
				name = "chromosome_" + str(i+1)
				numb = i+1
			
			print(name)	
			
			list_composite = [c for c in by_chromosome[i] if c in all_vs_all]
			nb_composite_both = len(list_composite)
			
			#print("ici \n", list_composite)
			
			comp, unique_comp = nb_components(list_composite, dico_composites, inv_dico_names)
			
			nb_families = composites_families(list_composite, inv_dico_names)
			
			nb_composite =  len(dico_comp_by_genes[numb])
			
			res.write("| " + name + " | " + str(list_nb_genes[i]) + " | " +str(nb_composite) + " | " + str(nb_composite_both) + " | " + str(comp) + "(" + str(unique_comp) + ")" + " | " + str(nb_families) + " | \n" )
		
		
if __name__ == "__main__":
	main()
	
	

