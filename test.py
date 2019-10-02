def myFun(name,*argv, **kwargs): 
    print ("First argument :", name) 
    for arg in argv:
        print("Next argument through *argv :", arg)


myFun('Hello','Welcome','to','Pleasure','dome', first = 'Geeks', mid='for', last = 'Geeks')

