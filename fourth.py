import os
import glob

for i, j, k in os.walk(r'C:\Users\roma\PycharmProjects\cinemas_parser\parse_cinemas'):
    # print(k)
    try:
        print(os.path.abspath(k[0]))
    except:
        print('---')

print('*' * 50)

for i in os.walk(r'C:\Users\roma\PycharmProjects\cinemas_parser\parse_cinemas'):
    print(i)




