from cx_Freeze import setup, Executable

executables = [Executable(r'c:\Users\roma\PycharmProjects\cinemas_parser\SCCScript.py',
                          icon='py.ico'
                          )
               ]

options = {
    'build_exe': {
        'include_msvcr': True,
    }
}

setup(name='sccscript',
      version='0.0.1',
      description='cray legacy',
      executables=executables
)