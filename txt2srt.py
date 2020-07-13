# written by deciMae, minorly edited by glumbaron

import sys

import tkinter as tk
import tkinter.filedialog as fd





numlines = 0
importf = ""
timedelta = 0
total = 0
updating = False
breakatchar = True


def openfile():
    global importf 
    global timedelta
    global total 
    
    importf = fd.askopenfilename()
    if(importf == ""): 
        return 0
    
    getnumlines()
    
    importfVar.set(importf)
    
    
    
    if(timedelta == 5 and total != 0):
        updatefromtotal()
    else:
        updatefromdelta()
    
    return importf

def getnumlines():
    global numlines
    if(importf == ""):
        numlines = 0
    else:
        numlines = sum(1 if line != "\n" else 0 for line in open(importf, "r"))
    numlinesVar.set(numlines)

def updatefromdelta(*args):
    global total
    global timedelta
    global updating

    if(updating):
        print("hi")
        return
    updating = True
    if((not timedeltaVar.get().isnumeric()) or int(timedeltaVar.get()) <= 0):
        timedeltaVar.set(str(timedelta))
    else :
        timedelta = int(timedeltaVar.get())
        if(importf != ""):
            total = timedelta * numlines
            seconds = total % 60
            totalsVar.set("%02d"% (seconds) )
            totalmVar.set(str(int(total/60)))
    updating = False

def updatefromtotal(*args):
    global updating 
    global timedelta
    global total

    if(updating):
        return
    updating = True
    if ( (not totalsVar.get().isnumeric()) or (not totalmVar.get().isnumeric()) or int(totalsVar.get()) > 59 or int(totalsVar.get()) < 0 or int(totalmVar.get()) < 0 or int(totalmVar.get()) + int(totalsVar.get()) == 0):
        seconds = total % 60
        totalsVar.set("%02d"% (seconds))
        totalmVar.set(str(int(total/60)))
    else:
        total = int(totalsVar.get()) + int(totalmVar.get())*60
        if(importf != ""):
            timedelta = int(total/numlines)
            timedeltaVar.set(str(timedelta))
    updating = False

def timestring(time, nexttime):
    hour = int(time / 3600)
    min = int(time / 60) % 60
    sec = int(time) % 60
    msec = int(time/1000) % 1000
    nexthour = int(nexttime / 3600)
    nextmin = int(nexttime / 60) % 60
    nextsec = int(nexttime) % 60
    nextmsec = int(time/1000) % 1000
    return ("%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n" %
                          (hour, min, sec, msec, nexthour, nextmin, nextsec, nextmsec))

def findchar(string,char):
    return [i for i, character in enumerate(string) if char == character]
    
def removeedgewhitespace(string):
    if(string[0] == " " or string[0] == "\n"):
        return removeedgewhitespace(string[1:])
    elif(string[-1] == " " or string[-1] =="\n"):
        return removeedgewhitespace(string[:-1])
    else:
        return string


def run():
    exportf = fd.asksaveasfilename(defaultextension = ".srt")
    file = open(importf, "r")
    outfile = open(exportf, "w")
    i = 0
    if(chopVar.get() == "charbreak"):
        readlength = int(maxcVar.get())
        minlength = int(mincVar.get())
        subsize = int(idcVar.get())
        numchars = len(file.read())
        file.seek(0)
        while(True):
            pos = subsize
            string = file.read(readlength + 1) # maybe read differently, getting the robot characters widths? 
            
            if(len(string) < readlength + 1):
                break
                
            short = string[minlength:-2]
            posits = findchar(short,"\n")
            if(posits):
                if([i for i in posits if string[posits + minlength + 1] == "\n"]):
                    pos = min([i for i in posits if string[posits + minlength + 1] == "\n"])   
            if(not posits):
                posits = findchar(short,".") + findchar(short,"!")
                if(not posits):
                    posits = findchar(short,",") + findchar(short,";") + findchar(short,":")
                    if(not posits):
                        posits = findchar(short," ")
                        
            if(posits):
                pos = min(posits, key = lambda t: abs(t - subsize)) + minlength # grab the closest 
            else:
                pos = subsize # gives up and just cuts 
            
            if(pos + 1< len(string)):
                if(string[pos+1] == "\n" or string[pos+1] == " "):
                    file.seek(file.tell() -readlength + pos + 1)
                else:
                    file.seek(file.tell() -readlength + pos)
            
            outfile.write(str(i)+ "\n")
            time = i * timedelta
            nexttime = (i + 1) * timedelta
            outfile.write(timestring(time, nexttime))
            outfile.write(string[:pos + 1] + "\n")
            i += 1
            
        if(string != ""):
            outfile.write(str(i) + "\n")
            time = i * timedelta
            nexttime = (i + 1) * timedelta
            outfile.write(timestring(time, nexttime))
            outfile.write(string[:pos + 1] + "\n")
            
            
            
        
        
        
    elif(chopVar.get() == "valbreak"):
        filechars = file.read() + "\n"
        numchar = len(filechars) - 1
        basewidth = float(deltacVar.get())
        bestlength = float(idcVar.get())
        
        scores = [[0,0] for i in range(numchar + 3)]
        
        
        for i in reversed(range(numchar-2)):
            listmin = i + 1
            listmax = min(int(round(i + bestlength + 3*basewidth)),numchar - 1)
            ideal = i + bestlength # could be float, that's okay

            
            

            
            for j in range(listmin, min(listmax + 1,numchar - 1)):
                if(filechars[j] == filechars[j + 1] and filechars[j] == "\n"):
                    listmax = j
                    break
                
            scoreopts = [[k,100] for k in range(listmin,listmax + 1)]
            for k in range(listmin, listmax + 1):
                if(filechars[k] == "\n" or filechars[k] == "." or filechars[k] == "!"):
                    scoreopts[k-listmin] = [k,0.001 + ((k - ideal)/basewidth)**2 + scores[k + 1][1]] # very slightly prefer less chops
                elif(filechars[k] == "," or filechars[k] == ";" or filechars[k] == ":"):
                    scoreopts[k-listmin] = [k,1.001 + ((k - ideal)/basewidth)**2 + scores[k + 1][1]]
                elif(filechars[k] == " "):
                    scoreopts[k-listmin] = [k,2.001 + ((k - ideal)/basewidth)**2 + scores[k + 1][1]]
            
            scores[i] = min(scoreopts, key = lambda pair : pair[1])

        l = 0
        i = 0
        while(scores[i][0] != 0): # why must python not do real for loops
            outfile.write(str(l) + "\n")
            time = l * timedelta
            nexttime = (l + 1) * timedelta
            outfile.write(timestring(time, nexttime))
            
            outfile.write(removeedgewhitespace(filechars[i:scores[i][0] + 1]) + "\n\n")
            i = scores[i][0] + 1
            l += 1
                
            
    else:
        for x in file:
            if x == "\n":
                continue
            outfile.write(str(i) + "\n")
            time = i * timedelta
            nexttime = (i + 1) * timedelta
            outfile.write(timestring(time, nexttime))
            outfile.write(x + "\n\n")
            i += 1
    exit()
    



window = tk.Tk()
window.title("txt2srt")
window.resizable(False,False)

tk.Label(window, text = "Import from:").grid(row = 0,column = 0)
importfVar = tk.StringVar()
tk.Entry(window, width = 60, textvariable = importfVar, state = "disabled").grid(row = 0, column = 1,columnspan = 5)
tk.Button(window, text = "Select", command = openfile).grid(row = 0, column = 6, columnspan = 3)

tk.Label(window, text = "Time per line (seconds):").grid(row = 1, column = 0)
timedeltaVar = tk.StringVar()
timedeltaVar.set("5")
timedeltaVar.trace("w",updatefromdelta)
tk.Entry(window, width = 5, validate = "focusout", textvariable = timedeltaVar, justify = "right").grid(row = 1, column = 1)

chopVar = tk.StringVar()
chopVar.set("linebreak")
tk.Radiobutton(window, text = "Use linebreaks to chop", variable = chopVar, value = "linebreak").grid(row = 2)

tk.Label(window, text = "Number of lines:").grid(row = 3, column = 0, columnspan = 2)
numlinesVar = tk.IntVar()
tk.Entry(window, width = 5, textvariable = numlinesVar, state = "disabled", justify = "right").grid(row = 3, column = 2)

tk.Label(window, text = "Time per line (seconds):").grid(row = 3, column = 3)
timedeltaVar = tk.StringVar()
timedeltaVar.set("5")
timedeltaVar.trace("w",updatefromdelta)
tk.Entry(window, width = 5, validate = "focusout", textvariable = timedeltaVar, justify = "right").grid(row = 3, column = 4)

tk.Label(window, text = "Total time (min:seconds)").grid(row = 3, column = 5)
totalmVar = tk.StringVar()
totalmVar.set("0")
totalmVar.trace("w",updatefromtotal)
tk.Entry(window, width = 5, validate = "focusout", textvariable = totalmVar, justify = "right").grid(row = 3, column = 6)

tk.Label(window, text = ":").grid(row = 3, column = 7)
totalsVar = tk.StringVar()
totalsVar.set("00")
totalsVar.trace("w",updatefromtotal)
tk.Entry(window, width = 2, validate = "focusout", textvariable = totalsVar, justify = "right").grid(row = 3, column = 8)

tk.Radiobutton(window, text = "Chop based on number of characters (force new caption with double newline)", variable = chopVar, value = "charbreak").grid(row = 4, columnspan = 4)

tk.Label(window, text = "Min characters:").grid(row = 5, column  = 0, columnspan = 2)
mincVar = tk.StringVar()
mincVar.set("65")
tk.Entry(window, width = 3, textvariable = mincVar, justify = "right").grid(row = 5, column = 2)

tk.Label(window, text = "Max:").grid(row = 5, column = 3)
maxcVar = tk.StringVar()
maxcVar.set("90")
tk.Entry(window,width = 3, textvariable = maxcVar, justify = "right").grid(row = 5, column = 4)

tk.Label(window, text = "Ideal characters:").grid(row = 5, column = 5)
idcVar = tk.StringVar()
idcVar.set("80")
tk.Entry(window, width = 3, textvariable = idcVar, justify = "right").grid(row = 5, column = 6)

tk.Radiobutton(window, text = "Chop based on score based on number of characters (force new caption with double newline)", variable = chopVar, value = "valbreak").grid(row = 6, columnspan = 5)

tk.Label(window, text = "Ideal characters:").grid(row = 7, column = 0)
idcVar = tk.StringVar()
idcVar.set("80")
tk.Entry(window, width = 5, textvariable = idcVar, justify = "right").grid(row = 7, column = 1)

tk.Label(window, text = "Character number deviation:").grid(row = 7, column = 2)
deltacVar = tk.StringVar()
deltacVar.set("10")
tk.Entry(window, width = 5, textvariable = deltacVar, justify = "right").grid(row = 7, column = 3)


tk.Button(window, text = "Convert", command = run).grid(row = 8, column = 6, columnspan = 3)
window.mainloop()



# old code, only here to conveniently restore command line functionality later 
# exportf = sys.argv[2]
# importf = sys.argv[1]
# if len(sys.argv) - 1 == 3:
    # maxmins, maxsecs = sys.argv[3].split(":")
    # maxtime = int(maxmins) * 60 + int(maxsecs)
# else:
    # maxtime = 0

# try:
    # file = open(importf, "r")
# except:
    # print("Error: file not found")

# numlines = sum(1 if line != "\n" else 0 for line in open(importf, "r"))

# if maxtime != 0:
    # timedelta = maxtime / numlines
# else:
    # timedelta = 2

# outfile = open(exportf, "w")
# i = 0
# for x in file:
    # if x == "\n":
        # continue
    # outfile.write(str(i) + "\n")
    # time = i * timedelta
    # nexttime = (i + 1) * timedelta
    # hour = int(time / 3600)
    # min = int(time / 60) % 60
    # sec = int(time) % 60
    # nexthour = int(nexttime / 3600)
    # nextmin = int(nexttime / 60) % 60
    # nextsec = int(nexttime) % 60
    # outfile.write("%02d:%02d:%02d,000 --> %02d:%02d:%02d,000\n" %
                  # (hour, min, sec, nexthour, nextmin, nextsec))
    # outfile.write(x + "\n")
    # i += 1