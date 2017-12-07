# -*- mode: python -*-

block_cipher = None


a = Analysis(['exrio\\__main__.py'],
             pathex=['G:\\shared\\git\\python-exrio','G:\\shared\\git\\python-exrio\\env\\Lib\\site-packages'],
             binaries=None,
             datas=None,
             hiddenimports=['OpenEXR'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='exrio',
          debug=False,
          strip=False,
          upx=True,
          console=True )
