import crayon

fileOpen = input("Enter file directory: ")
with open(fileOpen, 'r') as f:
    fileLines = f.readlines()
    codeLines = list(enumerate(fileLines))
    codeDict = dict(codeLines)
    crayon.executeProgram(codeDict)




