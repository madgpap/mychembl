#! /usr/bin/env python

## Reads molfiles from the ChEMBL db, generates images and stores them back in the db.

import psycopg2
from rdkit.Chem import Draw
from rdkit.Chem import AllChem as Chem
import cStringIO
import base64

conn = psycopg2.connect("port=5432 user=chembl dbname=chembl_17")
cur = conn.cursor()

#cur.execute("""SELECT mr.molregno, cs.molfile
#FROM compound_structures cs, mols_rdkit mr
#where
#mr.molregno=cs.molregno
#and mr.molregno not in (select molregno from mol_pictures)
#limit 2000""")

cur.execute("""select mm.molregno, cs.molfile
from (select m.molregno from mols_rdkit m except select p.molregno from mol_pictures p) mm,
compound_structures cs
where mm.molregno = cs.molregno
""")

print "Fetching the molregnos and mol files from the database ..."
count = 0
for d in list(cur):
    count += 1
    name = d[0]
    try:
        mol = Chem.MolFromMolBlock(d[1])
        mol.Compute2DCoords()
        image = Draw.MolToImage(mol)
    except:
        print "problem with molregno {0}, skipping...".format(name)
        continue
    buffer = cStringIO.StringIO()
    image.save(buffer, format="PNG")

    png = buffer.getvalue()
    #b64png = base64.b64encode(buffer.getvalue())

    numName = int(name)
    cur.execute("INSERT INTO mol_pictures VALUES (%d, %s)" % (numName, psycopg2.Binary(png)))
    if count % 1000 == 0:
        conn.commit()
        print "Inserting molregno {0} ...".format(name)

## Close connection
cur.close()
conn.commit()
conn.close()