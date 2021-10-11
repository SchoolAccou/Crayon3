def romanNum(  input  ):
  if not isinstance(input, int):
    raise TypeError("Roman Numeral input value must be an integer")
  else:
    value = abs(input)
    roman_numeral = []
    if input < 0:
        roman_numeral.append('-')
    if input == 0:
        roman_numeral.append('ZERO')
    #Thousands
    for i in range(value//1000):
      roman_numeral.append('M')
      value -= 1000
    #Hundreds
    for i in range(value//900):
      roman_numeral.append('CM')
      value -= 900
    for i in range(value//500):
      roman_numeral.append('D')
      value -= 500
    for i in range(value//400):
      roman_numeral.append('CD')
      value -= 400
    for i in range(value//100):
      roman_numeral.append('C')
      value -= 100
    #Tens
    for i in range(value//90):
      roman_numeral.append('XC')
      value -= 90
    for i in range(value//50):
      roman_numeral.append('L')
      value -= 50
    for i in range(value//40):
      roman_numeral.append('XL')
      value -= 40
    for i in range(value//10):
      roman_numeral.append('X')
      value -= 10
    #ones
    for i in range(value//9):
      roman_numeral.append('IX')
      value -= 9
    for i in range(value//5):
      roman_numeral.append('V')
      value -= 5
    for i in range(value//4):
      roman_numeral.append('IV')
      value -= 4
    for i in range(value//1):
      roman_numeral.append('I')
      value -= 1

  return("".join(roman_numeral))
