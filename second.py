from re import fullmatch

result = fullmatch(r'\d\d\d\d\d\d', '123456')

if result:
    print(True)
else:
    print(False)