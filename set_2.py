letter_values = {
    'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6,
    'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13,
    'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20,
    'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25,
}

def shift_letter(letter, shift):
    if letter == " ":
        return " "
    if letter in letter_values:
        new_value = (letter_values[letter] + shift) % 26
        for key, value in letter_values.items():
            if value == new_value:
                return key
    return ""

def caesar_cipher(text, shift):
    result = ""
    for char in text:
        result += shift_letter(char, shift)
    return result


def shift_by_letter(letter, shift_letter):
    if letter == " ":
        return " "
    if letter in letter_values and shift_letter in letter_values:
        new_value = (letter_values[letter] + letter_values[shift_letter]) % 26
        for key, value in letter_values.items():
            if value == new_value:
                return key
    return ""

def vigenere_cipher(message, key):
    result = ""
    key_index = 0
    for char in message:
        if char == " ":
            result += " "
        elif char in letter_values:
            key_char = key[key_index % len(key)]
            result += shift_by_letter(char, key_char)
        key_index += 1
    return result

def scytale_cipher(message, shift):
    if len(message) % shift != 0:
          message += "_" * (shift - len(message) % shift)
    
    result = ""
    for i in range(len(message)):
        index = (i // shift) + (len(message) // shift) * (i % shift)
        result += message[index]
    return result

def scytale_decipher(message, shift):
    result = ""
    for i in range(len(message)):
        index = (i // (len(message) // shift)) + (i % (len(message) // shift)) * shift
        result += message[index]
    return result
