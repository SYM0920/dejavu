import subprocess
import pandas as pd
import os

# df = pd.read_csv('m_p.csv')

files = ['ABC605813_ara.wav', 'ABC605813_dut.wav', 'ABC605813_gre.wav', 'ABC605813_ind.wav', 'ABC605813_m_e.wav', 'ABC605813_pol.wav', 'ABC605813_spa.wav', 'ABC605813_bpr.wav', 'ABC605813_heb.wav', 'ABC605813_las.wav', 'ABC605813_mnd.wav', 'ABC605813_por.wav', 'ABC605813_swe.wav', 'ABC605813_dan.wav', 'ABC605813_ger.wav', 'ABC605813_hun.wav', 'ABC605813_may.wav', 'ABC605813_nor.wav', 'ABC605813_rus.wav', 'ABC605813_tur.wav']

def subprocess_cmd(command):
	process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
	proc_stdout = process.communicate()[0].strip()
	print(proc_stdout)

for file in files:
	subprocess_cmd('python3 auto_qc_noneng2.py --english {} --nonenglish {} --is_non_conformed {}'.format('proxy/ABC605813_eng.wav', 'proxy/' + file, 0))
