import sqlite3
conn = sqlite3.connect('clients.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE clients
             (date, time, name, phone)''')

# data to be added
test_client = ('1001-01-01', '00:00:00', 'John', '88005553535')

# add data
c.execute('INSERT INTO clients VALUES (?,?,?,?)', test_client)

# Save (commit) the changes
conn.commit()

# end connection
conn.close()
