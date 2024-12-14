import re

def punctuation_validation(text: str) -> bool:
    # проверка на корректную расстановку знаков препинания
    for i in range(0, len(text) - 1):
        # пробел или спец символ после знака препинания
        if text[i] in [',', '.', '!', '?', ':', ';', '\''] and text[i + 1] not in (' ', '\t', '\n'):
            return False
        # двойная кавычка внутри слова
        if text[i] == "\"" and text[i + 1] not in (' ', '\t', '\n') and text[i - 1] not in (' ', '\t', '\n'):
            return False
        # один пробел
        if text[i] == " " and text[i + 1] == " ":
            return False
    return True

def uppers_validation(words: list) -> bool:
    # проверка на корректную расстановку заглавных букв:
    # допустимо: чтобы слова начинались с заглавной
    # недопустимо: заглавные буквы посреди слова, если само слово состоит из строчных букв
    # для проверки отсекаем первую букву слова
    for word in words:
        base = word[1:]
        if len(base) == 0:
            continue

        only_lowers = base.islower()
        only_uppers = base.isupper()
        # если слово начинается с заглавной и продолжается строчными, то оно может быть именем собственным, или первым словом в предложении
        if word[0].isupper() and only_lowers:
            continue
        # в обратном случае, если первая буква строчная, а остальные заглавные - это некорректно
        if word[0].islower() and only_uppers:
            return False
        # проверка на то, чтобы все буквы были одного регистра
        if not only_uppers and not only_lowers:
            return False

    return True

def readability_validation(words: list, english_vocabulary: list) -> bool:
    for i, word in enumerate(words):
        readable = False
        for voc_word in english_vocabulary:
            # если слово в тексте одно, то оно может быть либо началом, либо окончанием
            if len(words) == 1:
                if str(voc_word).endswith(word.lower()) or str(voc_word).startswith(word.lower()):
                    readable = True
                    break
            elif i == 0:
                # первое слово в тексте является частью слова
                if str(voc_word).endswith(word.lower()):
                    readable = True
                    break
                # проверяем, может ли быть слово именем собственным (или его частью)
                if str.isupper(word[0]) == True and str.islower(word[1:]) == True:
                    readable = True
                    break
            elif i == len(words) - 1:
                # последнее слово в тексте является частью слова
                if str(voc_word).startswith(word.lower()):
                    readable = True
                    break
                # проверяем, может ли быть слово именем собственным (или его частью)
                if str.isupper(word[0]) == True and str.islower(word[1:]) == True:
                    readable = True
                    break

            # для остальных слов должно быть точное совпадение со словом из словаря
            else:
                # если слово состоит из одной буквы, то проверяем является ли оно местоимением "I" или артиклем "a"
                if len(str.lower(word)) == 1:
                    if word != "a" and word != "i":
                        return False

                # проверяем на имя собственное
                if str.isupper(word[0]) == True and str.islower(word[1:]) == True:
                    readable = True
                    break

                # проверяем на наличие точного совпадения в словаре
                if str.lower(word) == str(voc_word):
                    readable = True
                    break

    return readable


def word_validation(text: str, english_vocabulary: list) -> bool:
    if not punctuation_validation(text):
        return False

    # выделяем слова из дешифруемого текста
    regex_pattern = '|'.join(map(re.escape, [".", "?", "!", ",", ":", ";", "'", "\n", "\t", "\"", " ", "_"]))
    text_splits = re.split(regex_pattern, text, maxsplit=0)
    words = [word for word in text_splits if word != ' ' and word != '']

    # проверка на корректную расстановку заглавных букв
    if not uppers_validation(words):
        return False

    # проверяем, что образованные сочетания букв - части существующих слов английского
    if not readability_validation(words, english_vocabulary):
        return False

    # если все проверки пройдены - возвращаем истину
    return True