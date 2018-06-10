from cx_Freeze import setup, Executable

executables = [Executable(r'C:\Users\medvet\PycharmProjects\cinemas_parser\createActiveStat.py')]

setup(name='active_stat',
      version='0.0.1',
      description='active_stat_creator',
      executables=executables
)