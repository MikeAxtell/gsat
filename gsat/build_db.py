import sqlite3
import os.path
import sys
import re
import csv

def build_db(mfile, odir, metadata, md_factors):
    # file checks
    # libinfo.csv should be produced by any type of run.
    libinfoFile = odir.rstrip("/") + '/libinfo.csv'
    if not os.path.isfile(libinfoFile):
        print("Database build failed.")
        print("Failed to find required file", libinfoFile)
        sys.exit()

    # This will be ABSENT in runs using pre-trimmed reads
    triminfoFile = odir.rstrip("/") + '/triminfo.csv'
    #if not os.path.isfile(triminfoFile):
        #print("Database build failed.")
        #print("Failed to find required file", triminfoFile)
        #sys.exit()

    # This will be ABSENT in runs that don't specify mature queries
    #if not os.path.isfile(mfile):
        #print("Database build failed.")
        #print("Failed to find required file", mfile)
        #sys.exit()

    # Metadata are required for any type of run, so this is OK
    if not os.path.isfile(metadata):
        print("Database build failed.")
        print("Failed to find required file", metadata)
        sys.exit()

    # Connect to / create the database
    if os.path.isfile(mfile):
        sqlbase = re.sub('.mature.csv$', '', mfile)
        sqlbase2 = re.sub('^.*\/', '', sqlbase)
        sqliteFile = odir.rstrip("/") + '/' + sqlbase2 + '.sqlite'
    else:
        sqliteFile = odir.rstrip("/") + '/' + 'gsat.sqlite'

    # Stop here if the database already exists
    if os.path.isfile(sqliteFile):
        return sqliteFile

    conn = sqlite3.connect(sqliteFile)
    c = conn.cursor()

    # Create table libinfo
    c.executescript("""
        CREATE TABLE libinfo(
            sample TEXT,
            countType TEXT,
            size INTEGER,
            firstBase TEXT,
            count INTEGER
        );
        """)
    # Populate table libinfo
    toInsert = []
    with open(libinfoFile) as lf:
        reader = csv.DictReader(lf)
        for row in reader:
            x = (row['sample'],
                 row['countType'],
                 int(row['size']),
                 row['firstBase'],
                 int(row['count']))
            toInsert.append(x,)
    c.executemany('INSERT INTO libinfo VALUES (?,?,?,?,?)', toInsert)

    # Create table triminfo, if warranted
    if os.path.isfile(triminfoFile):
        c.executescript("""
            CREATE TABLE triminfo(
                sample TEXT,
                category TEXT,
                count INTEGER
            );
            """)
        # Populate table triminfo
        toInsert = []
        with open(triminfoFile) as tf:
            reader = csv.DictReader(tf)
            for row in reader:
                x = (row['sample'],
                     row['category'],
                     int(row['count']))
                toInsert.append(x,)
        c.executemany('INSERT INTO triminfo VALUES (?,?,?)', toInsert)

    # Create table mature, index it by matureName, if warranted
    if os.path.isfile(mfile):
        c.executescript("""
            CREATE TABLE mature(
                sample TEXT,
                matureName TEXT,
                sequence TEXT,
                editDistance INTEGER,
                raw INTEGER,
                rpm REAL
            );
            CREATE INDEX nameidx ON mature(matureName);
            """)
        # Populate table mature
        toInsert = []
        with open(mfile) as mf:
            reader = csv.DictReader(mf)
            for row in reader:
                x = (row['sample'],
                     row['matureName'],
                     row['sequence'],
                     int(row['editDistance']),
                     int(row['raw']),
                     float(row['rpm']))
                toInsert.append(x,)
        c.executemany('INSERT INTO mature VALUES (?,?,?,?,?,?)', toInsert)
    
    # Create table metadata
    mstatement = 'CREATE TABLE metadata(sample TEXT'
    q = ['?']  ## for the sample
    for idx in md_factors:
        mstatement = mstatement + ',' + md_factors[idx] + ' TEXT'
        q.append('?')
    mstatement = mstatement + ')'
    c.execute(mstatement)

    # Populate table metadata
    with open(metadata) as md:
        line_n = 0
        toInsert = []
        for line in md:
            line_n += 1
            if line_n > 1:
                line = line.strip()
                x = tuple(line.split(','))
                toInsert.append(x,)
    qs = ','.join(q)
    ex = 'INSERT INTO metadata VALUES (' + qs + ')'
    # test
    #print("x:", x)
    c.executemany(ex, toInsert)    

    # Clean up
    conn.commit()
    conn.close()

    # return the file
    return sqliteFile
    
    
            
        
    
    

    


    
    

    

    
    
    
