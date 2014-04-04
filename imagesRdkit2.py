#! /usr/bin/env python

import psycopg2
from rdkit.Chem import Draw
from rdkit.Chem import AllChem as Chem
import subprocess

conn=psycopg2.connect("port=5432 user=user dbname=chembl_15")
cursor = conn.cursor()
print "Fetching the molregno from the database ..."
cursor.execute("SELECT molregno FROM mols_rdkit where molregno not in (select molregno from mol_pictures) ORDER BY molregno ASC")
molregno = cursor.fetchall()
count = 0
for molecule in molregno:
    count += 1
        if count % 1000 == 0:
                conn.commit()
        query=molecule[0]
    cursor.execute("SELECT mr.molregno,cs.molfile FROM compound_structures cs, mols_rdkit mr where mr.molregno=cs.molregno and mr.molregno=%s" %query)
    records=cursor.fetchall()
    for data in records:
            name=data[0]
            fileName=str(name)+".png"
            path="/var/www/compound_images/"+fileName

            if count % 1000 == 0:
                print "Inserting molregno %s ..." %name
            mol= Chem.MolFromMolBlock(data[1])
            mol.Compute2DCoords()
            Draw.MolToFile(mol,path)
    
            numName=int(name)
            cursor.execute("INSERT INTO mol_pictures VALUES (%d,lo_import('%s'))" %(numName,path))
            subprocess.call(["rm","-f",path])

# Close connection
cursor.close()
conn.commit()
conn.close()