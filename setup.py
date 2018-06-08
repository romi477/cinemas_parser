from cx_Freeze import setup, Executable

executables = [Executable(r'C:\Users\roma\PycharmProjects\cinemas_parser\getStatData.py')]

setup(name='cinemas_parser',
      version='0.0.1',
      description='my_cinemas_parser',
      executables=executables
)