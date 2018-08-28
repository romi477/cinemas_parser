import subprocess


activCmd = r'Tools\XmlSigner.exe -sign -key Tools\ActivationKey.RSAPrivate -file Activation.xml.xml'
statCmd = r'Tools\XmlSigner.exe -sign -key Tools\OwnerIDSignKey.RSAPrivate -file Statistics.key.xml'
compressActiv = r'Tools\Compressor.exe compress Activation.xml.xml Activation.xml -mtf'
compressStat = r'Tools\Compressor.exe compress Statistics.key.xml Statistics.key -mtf'


def sign_compress(cmd, compress):
    sign = subprocess.run(cmd, shell=True)
    if sign.returncode == 0:
        code = subprocess.run(compress)
        if code.returncode == 0: print('function ok')
        else: print('compress fail')
    else: print('sign fail')


sign_compress(activCmd, compressActiv)
sign_compress(statCmd, compressStat)
