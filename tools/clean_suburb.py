file = "Suburb Locality.csv"
out = ""
flag = True
with open("suburbs.csv","w") as fd1:
    with open(file,"r") as fd2:
        for line in fd2:
            if flag:
                flag = False
            else:
                fd1.write(line.split(",")[0]+",")