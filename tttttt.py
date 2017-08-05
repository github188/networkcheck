import os,sys
xls_dir = os.path.split(os.path.realpath(sys.argv[0]))[0] + "\\logs\\longping\\"
xlsfile = os.path.join(xls_dir,"longpingdata.xlsx")
print(xlsfile)
if os.path.exists(xlsfile):
    print("11")
    os.system(xlsfile)