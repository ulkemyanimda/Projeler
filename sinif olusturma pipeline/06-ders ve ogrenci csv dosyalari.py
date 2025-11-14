import pandas as pd
import os
from tabulate import tabulate

path="./YeniSiniflar/"
def find_the_way(path,file_format):
    files_add = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file_format in file:
                files_add.append(os.path.join(r, file))  
    return files_add
files_add=find_the_way(path,'.xlsx')
files_add


ders = [["shortname","fullname",	"category"]]
ogrenci=[["username",	"course1",	"role1"]]
for i in files_add:
    df=pd.read_excel(i)
    code=i[15:]
    temp=df["Orijinal_Dosya"].unique()[0]
    ders.append([code,temp,5])
    for j in  df["username"].values:
        ogrenci.append([j,code,"student"])
df = pd.DataFrame (ders[1:], columns = ders[0])
of = pd.DataFrame (ogrenci[1:], columns = ogrenci[0])
df.to_csv("dersler.csv", index=False)      
of.to_csv("ogrenciler.csv", index=False)


    