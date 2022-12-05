import sqlite3
conn = sqlite3.connect('rating.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE ratings
             (order_number, service, convenience, shoes)''')

# data to be added
purchases = [('2006-01-05', 123456, 'example@rasa.com', 'blue', 9, 'returning'),
             ('2021-01-05', 123457, 'me@rasa.com', 'black', 10, 'order pending'),
             ('2021-01-05', 123458, 'me@gmail.com', 'gray', 11, 'delivered'),
             ]

test = (123, 5, 5, 5)

# add data
c.execute('INSERT INTO ratings VALUES (?,?,?,?)', test)

# Save (commit) the changes
conn.commit()

# end connection
conn.close()
