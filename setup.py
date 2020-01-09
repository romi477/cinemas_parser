from cx_Freeze import setup, Executable

executables = [Executable(r'c:\Users\roma\PycharmProjects\cinemas_parser\SCCScript.py',
                          icon='py.ico'
                          )
               ]

packages = ['pyexcel', 'xlrd', 'xlwt']

options = {
    'build_exe': {
        'include_msvcr': True,
        'packages': packages
    }
}

setup(
    name='sccscript',
    options=options,
    version='0.0.1',
    description='cray legacy',
    executables=executables
)
