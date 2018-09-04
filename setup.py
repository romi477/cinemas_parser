from cx_Freeze import setup, Executable

executables = [Executable(r'c:\Users\medvet\PycharmProjects\cinemas_parser\createActivStat.py',
                          icon='py.ico'
                          )
               ]

options = {
    'build_exe': {
        'include_msvcr': True,
    }
}

setup(name='active_stat',
      version='0.0.1',
      description='active_stat_creator',
      executables=executables
)