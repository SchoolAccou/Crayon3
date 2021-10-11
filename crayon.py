import re
import sys
from romanNumerals import romanNum

# TODO: refactor regexes & commands into dictionary
execRegex = re.compile(r'(?<=##{).{1,}(?=}##)') #Defines execute command
printRegex = re.compile(r"(?<=displayOut\(\').{1,}(?=\'\))")
addRegex = re.compile(r"(?<=add\()[\d,\-,\+,\.]{1,}(?=\))")
statementRegex = re.compile(r"(?<=\$)[^\$]{1,}") #Statements must begin with '$'
varRegex = re.compile(r"(VAR\(([A-Za-z]+)\))") # VAR(<variable name>)
setVarRegex = re.compile(r"(?<=setVar\()NAME=([A-Za-z]+),VALUE=([^\)]{1,})(?=\))") #setVar(NAME=<variable name>,VALUE=<variable value>)
embedExecRegex = re.compile(r"(EMBED{([^}]+)}EMBED)") #Example statement: $displayOut('Your Name is: EMBED{userInput('What is your name?')}EMBED')
inputRegex = re.compile(r"(?<=userInput\(\').+(?=\'\))") #Input MUST HAVE a string
ifRegex = re.compile(r"(?<=if\()CONDITION=(True|False),TRIGGER=([A-Za-z0-9]+)(?=\))")#Example statement: $if(CONDITION=TRUE,TRIGGER=01)
evalRegex = re.compile(r"eval\('([^']+)'='([^']+)'\)")#Example statement: $eval('Hello'='Hello')
trigExecRegex = re.compile(r"TRIG\{(.+)\}TRIG\[([A-Za-z0-9]+)\]")#Example: TRIG{<code goes here>}TRIG[<Trigger Name>]
notIfRegex = re.compile(r"(?<=notIf\()CONDITION=(True|False),TRIGGER=([A-Za-z0-9]+)(?=\))")#opposite of if, disables trigger if CONDITION is TRUE, activates it if CONDITION is FALSE
arithRegex = re.compile(r"arith\((-?[0-9]*.?[0-9]+)([+,\-,*,/])(-?[0-9]*.?[0-9]+)\)") #syntax: arith(<number 1><operator><number 2>)
comparRegex = re.compile(r"compare\((-?[0-9]*.?[0-9]+)(<|>)(-?[0-9]*.?[0-9]+)\)") #syntax: compare(<number 1><operator><number 2>)
gotoRegex = re.compile(r"GOTO\(([0-9]+)\)") #syntax: GOTO(<line number>)
romanRegex = re.compile(r"rome\(([0-9]*.?[0-9]+)\)") #syntax: rome(<number>)
lenRegex = re.compile(r"len\((.+?)\)") #syntax: len(<string>)
dictRegex = re.compile(r"newDict\(NAME=([A-Za-z]+)\)") #syntax: newDict(NAME=<dictionary name>)
editDictRegex = re.compile(r"editDict\(DICT=([A-Za-z]+)\,KEY=([A-Za-z0-9]+)\,VALUE=(.+?)\)") #syntax: editDict(DICT=<dictionary>,KEY=<key>,VALUE=<value>)
getDictRegex = re.compile(r"getDict\(DICT=([A-Za-z]+)\,KEY=([A-Za-z0-9]+)\)") #syntax: getDict(DICT=<dictionary>,KEY=<key>)
indexRegex = re.compile(r"index\(STRING='(.+?)',INDEX=([0-9]+)\)") #syntax: index(STRING='<string>',INDEX=<index number>)
intRegex = re.compile(r'int\((-?[0-9]*.?[0-9]+)\)')#syntax: int(<number>)


variables = []

triggers = []

dicts = dict()

linecount = 0
def executeProgram(lines):
    global linecount
    """
    Initializes all elements in a list
    (for GOTO statements)
    Takes dictionary as input
    """
    totalLines = len(lines)
    while linecount < totalLines:
        initialize(lines.get(linecount))
        linecount += 1

def boolString(string):
    """
    parses strings into booleans
    """
    if string == "True":
        return True
    else:
        return False

    

class Trigger():
    def __init__(self, name=None, value=False):
        self.name = name
        self.value = value

class Variable():
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
    

def initialize(codeVar):
    """
    Handles execution commands such as ## and TRIG
    """
    runOne = execRegex.search(codeVar) #Executes ##
    if runOne is not None:
        parseStatements(runOne.group(0))

    runTwo = trigExecRegex.search(codeVar) #Executes TRIG
    if runTwo is not None:
        for trigger in triggers:
            if trigger.name == runTwo.group(2) and trigger.value is True:
                parseStatements(runTwo.group(1))

def variableParse(codeVar):
    """
    parses variables
    """
    variableTagList = varRegex.findall(codeVar) #returns a list of tuples. variableTag[0] is equivalent to group(0), variableTag[1] is equivalent to group(1), etc.
    output = codeVar
    for variableTag in variableTagList:
        for variable in variables:
            if variable.name == variableTag[1]:
                output = output.replace(variableTag[0], variable.value)
    return output

def embedParse(codeVar):
    """
    Parses Embedded Code
    """
    embedList = embedExecRegex.findall(codeVar)
    output = codeVar
    for embed in embedList:
        embedOutput = embedExecute(embed[1])
        if embedOutput is not None:
            output = output.replace(embed[0], embedOutput)
    return output




def parseStatements(codeVar):
    """
    Detects individual statements in an execute command
    """
    statements = statementRegex.findall(codeVar)
    for statement in statements:
        varParseStatement = variableParse(statement)
        embedStatement = embedParse(varParseStatement)
        execute(embedStatement)

def embedExecute(codeVar):
    """
    Executes embedded code
    """
    output = None
    if inputRegex.search(codeVar) is not None:
        output = inputCommand(codeVar)
    if evalRegex.search(codeVar) is not None:
        output = evalCommand(codeVar)
    if arithRegex.search(codeVar) is not None:
        output = arithCommand(codeVar)
    if comparRegex.search(codeVar) is not None:
        output = compareCommand(codeVar)
    if romanRegex.search(codeVar) is not None:
        output = romanNumCommand(codeVar)
    if lenRegex.search(codeVar) is not None:
        output = lenCommand(codeVar)
    if getDictRegex.search(codeVar) is not None:
        output = getDictCommand(codeVar)
    if indexRegex.search(codeVar) is not None:
        output = indexCommand(codeVar)
    if intRegex.search(codeVar) is not None:
        output = intCommand(codeVar)
    return output
    
def inputCommand(codeVar):
    """
    User input function
    Embeddable = YES
    """
    inputSearch = inputRegex.search(codeVar)
    if inputSearch is None:
        return None
    
    output = input(inputSearch.group(0))
    return output
    
def execute(codeVar):
    """
    Executes parsed statements
    """
    printCommand(codeVar)
    exitCommand(codeVar)
    addCommand(codeVar)
    howSayCrayon(codeVar)
    setVar(codeVar)
    ifCommand(codeVar)
    notIfCommand(codeVar)
    gotoCommand(codeVar)
    newDictCommand(codeVar)
    editDictCommand(codeVar)


def addCommand(codeVar):
    """
    performs addition
    NOTE:
    This command is outdated. it is recommended that you use arith() instead.
    """
    addRun = addRegex.search(codeVar)
    if addRun is None:
        return
    addNums = re.split(r'\+', addRun.group(0))
    addFloats = []
    for ele in addNums:
        addFloats.append(float(ele))
    output = 0
    for ele in addFloats:
        output += ele
    print(output)
    

def printCommand(codeVar):
    #Defines print statement
    printRun = printRegex.search(codeVar)
    if printRun is None:
        return
    print(printRun.group(0))

def exitProg(exitCause):
    """
    Defines exit
    """
    sys.exit(f"Crayon Process Terminated: {exitCause}")

def exitCommand(codeVar):
    if 'EXIT' in codeVar:
        exitProg("EXIT_COMMAND")

def howSayCrayon(codeVar):
    if 'HOW_SAY_CRAYON' in codeVar:
        print("Here is how you say Crayon: KRAE-OHN")

def setVar(codeVar):
    varSetRun = setVarRegex.search(codeVar)
    if varSetRun is None:
        return
    variableExists = False
    for variable in variables:
        if variable.name == varSetRun.group(1): 
            variableExists = True
            variable.value = varSetRun.group(2)
    if not variableExists:
        variables.append(Variable(name=varSetRun.group(1), value=varSetRun.group(2)))

def evalCommand(codeVar):
    """
    Evaluates a statement as true or false
    Is embeddable
    """
    evalSearch = evalRegex.search(codeVar)
    if evalSearch is None:
        return None
    if evalSearch.group(1) == evalSearch.group(2):
        return 'True'
    return 'False'

def ifCommand(codeVar):
    """
    Takes a boolean and executes code if it is true
    """
    ifSearch = ifRegex.search(codeVar)
    if ifSearch is not None:
        triggerExists = False
        for trigger in triggers:
            if trigger.name == ifSearch.group(2):
                trigger.value = boolString(ifSearch.group(1))
                triggerExists = True
        if not triggerExists:
            newTrig = Trigger(name=ifSearch.group(2), value=boolString(ifSearch.group(1)))
            triggers.append(newTrig)

def notIfCommand(codeVar):
    """
    Takes a boolean and executes code if it is false,
    opposite of if command
    """
    notIfSearch = notIfRegex.search(codeVar)
    if notIfSearch is not None:
        triggerExists = False
        for trigger in triggers:
            if trigger.name == notIfSearch.group(2):
                trigger.value = not boolString(notIfSearch.group(1))
                triggerExists = True
        if not triggerExists:
            newTrig = Trigger(name=notIfSearch.group(2), value=not boolString(notIfSearch.group(1)))
            triggers.append(newTrig)

def arithCommand(codeVar):
    """
    Performs Arithmetic
    Is Embeddable
    """
    arithSearch = arithRegex.search(codeVar)
    if arithSearch.group(2) == '+':
        return str(float(arithSearch.group(1)) + float(arithSearch.group(3)))
    elif arithSearch.group(2) == '-':
        return str(float(arithSearch.group(1)) - float(arithSearch.group(3)))
    elif arithSearch.group(2) == '*':
        return str(float(arithSearch.group(1)) * float(arithSearch.group(3)))
    elif arithSearch.group(2) == '/':
        return str(float(arithSearch.group(1)) / float(arithSearch.group(3)))

def compareCommand(codeVar):
    """
    Compares the value of two numbers
    Is Embeddable
    """
    compareSearch = comparRegex.search(codeVar)
    if compareSearch.group(2) == "<":
        return str(float(compareSearch.group(1)) < float(compareSearch.group(3)))
    elif compareSearch.group(2) == ">":
        return str(float(compareSearch.group(1)) > float(compareSearch.group(3)))

def gotoCommand(codeVar):
    """
    Sends execution back to a certain line (executeProgram only)
    """
    global linecount
    gotoSearch = gotoRegex.search(codeVar)
    if gotoSearch is not None:
        linecount = int(gotoSearch.group(1)) - 2 #line number is offset by 2 because dictionary IDs go up from zero and executeProgram() adds 1 linecount at the end of its loop

def romanNumCommand(codeVar):
    """
    converts input to roman numerals
    is embeddable
    """
    romanSearch = romanRegex.search(codeVar)
    return romanNum(int(romanSearch.group(1)))

def lenCommand(codeVar):
    """
    finds length of string
    is embeddable
    """
    lenSearch = lenRegex.search(codeVar)
    return str(len(lenSearch.group(1)))

def newDictCommand(codeVar):
    newDictSearch = dictRegex.search(codeVar)
    if newDictSearch is not None:
        dicts[newDictSearch.group(1)] = dict()

def editDictCommand(codeVar):
    """
    edits dictionaries
    """
    editDictSearch = editDictRegex.search(codeVar)
    if editDictSearch is None:
        return
    dictionary = dicts.get(editDictSearch.group(1))
    if dictionary is None:
        exitProg(f"editDict(): dictionary '{editDictSearch.group(1)}' does not exist")
    dictionary[editDictSearch.group(2)] = editDictSearch.group(3)

def getDictCommand(codeVar):
    """
    retrieves values from dictionaries
    IS EMBEDDABLE
    """
    getDictSearch = getDictRegex.search(codeVar)
    dictionary = dicts.get(getDictSearch.group(1))
    if dictionary is None:
        exitProg(f"getDict(): dictionary '{getDictSearch.group(1)}' does not exist")
    return str(dictionary.get(getDictSearch.group(2)))

def indexCommand(codeVar):
    """
    retrieves index of a string
    Is embeddable
    """
    indexSearch = indexRegex.search(codeVar)
    return indexSearch.group(1)[int(indexSearch.group(2))]

def intCommand(codeVar):
    """
    converts float to integer
    is embeddable
    """
    intSearch = intRegex.search(codeVar)
    return str(int(float(intSearch.group(1))))




    
    
        