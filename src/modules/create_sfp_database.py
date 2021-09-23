# Script to create a database of SFP information

import mysql.connector
from typing import List

def create_table(cursor):
    try:
        cursor.execute("CREATE TABLE sfp (id INT AUTO_INCREMENT PRIMARY KEY\
            , vendor_id VARCHAR(255), vendor_part_number VARCHAR(255), transceiver_type VARCHAR(255))")
    except Exception as ex:
        print("ERROR in create_table()")
        print(ex)
        return

def create_page_table(cursor, table_name: str):
    try:
        sql = f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, "
        
        for i in range(255):
            sql += f'`{i}` INT, '

        sql += '`255` INT);'

        #print(sql)

        cursor.execute(sql)

    except Exception as ex:
        print("Error in create_page_table()")
        print(ex)
        return

def insert_sfp_data_to_table(cursor, tablename: str, values: List[str]) -> None:
    
    sql_statement = f"select count(*) as count from information_schema.columns where table_name=\'{tablename}\'"
    cursor.execute(sql_statement)

    result = cursor.fetchone()
    # Remove auto-increment primary key
    columns_in_table = result[0] - 1

    if len(values) != columns_in_table:
        print(f'ERROR: Expected {columns_in_table} values to insert but got {len(values)}')
        return

    sql_statement = f"INSERT INTO {tablename} (vendor_id, vendor_part_number, transceiver_type) VALUES (%s, %s, %s)"
    vals = tuple(values)        

    cursor.execute(sql_statement, vals)
    
    # Also create entry in page table for this

    sql_statement = f'INSERT INTO page_a0 ('
    for i in range(255):
        sql_statement += f"`{i}`, "
    sql_statement += '`255`) VALUES ('
    for i in range(255):
        sql_statement += "%s, "
    sql_statement += "%s)"

    vals = [0] * 256
    vals = tuple(vals)
    cursor.execute(sql_statement, vals)

def read_sfp_memory_map(filepath: str) -> List[int]:
    '''
    Given a path to a .bin file containing SFP memory maps, reads
    the 
    '''
    mem_vals = []

    bin_file = open(filepath, 'rb')
    for line in bin_file:
        mem_vals = mem_vals + list(line)

    bin_file.close()


    if len(mem_vals) < 256:
        for _ in range(256 - len(mem_vals)):
            mem_vals.append(0)

    return mem_vals

def get_info_from_memory_map(memory_map: List[int]):
    pass

def main():
    
    mydb = mysql.connector.connect(
        host="localhost",
        user="connord",
        password="cloudplug",
        database="sfp_info"
    )

    mycursor = mydb.cursor()

    create_table(mycursor)
    create_page_table(mycursor, 'page_a0')

    #T= Testing insertion to database
    sql = "INSERT INTO sfp (vendor_id, vendor_part_number, transceiver_type) VALUES (%s, %s, %s)"
    vals = ("Raspberry Pi", "unknown", "QFBR-576LP")
    mycursor.execute(sql, vals)
    insert_sfp_data_to_table(mycursor, "sfp", list(vals))
    mydb.commit()
    print(mycursor.rowcount, "record inserted")

    print("\n\nReading all entries from sfp table")
    sql = "SELECT * from sfp"
    mycursor.execute(sql)

    myresult = mycursor.fetchall()

    for x in myresult:
        print(x)

    print('\n\nReading sfp memory')
    memory_map = read_sfp_memory_map('sfp3.bin')
    print(f'Length is {len(memory_map)}')

    '''
    memory_map2 = []
    print('Reading other file')
    with open('sfp_memory_map.bin') as file:
        for line in file:
            vals = line.split(',')
            for val in vals:
                if val != '\n':
                    print(int(val, 16), end=' ')
                    memory_map2.append(int(val, 16))

    for i, j in zip(memory_map, memory_map2):
        if i != j:
            raise Exception('Lists not equal')
    '''
    # Testing writing old data to binary file
    #with open('sfp2.bin', 'wb') as mem_file:
    #    vals = bytes(memory_map)
    #    mem_file.write(vals)

    

if __name__ == '__main__':
    main()