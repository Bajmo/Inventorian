file=open("myfile.txt","w")
file.write("helloo")
file.close





file2=open("myfile.txt","r")
for i in file2:
    print(i)
file2.close()