# -*- mode: python -*-

block_cipher = None


a = Analysis(['CCI_nw_checker.py'],
             pathex=['C:\\Users\\xuziheng\\Desktop\\已完成项目\\协作云网路自动化自检\\8.5.2'],
             binaries=[],
             datas=[],
             hiddenimports=[],
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
          name='CCI_nw_checker',
          debug=False,
          strip=False,
          upx=True,
          console=True )
