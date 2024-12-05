from dataclasses import dataclass
import string

class RussianLanguage:
    alphabet = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я']
    num_of_letters = len(alphabet)
    letters_dict = {letter: i for i, letter in enumerate(alphabet)}

    def e_replace(self, word: str) -> str:
        return word.replace('Ё', 'Е')

    def get_letter_by_order(self, letter_order : int) -> str:
        return RussianLanguage.alphabet[letter_order]

    def get_order_by_letter(self, letter: str) -> int:
        return RussianLanguage.letters_dict[letter]


class VigenereLengthFinder:
    def __init__(self, encrypted_text: str) -> None:
        self.russian_language = RussianLanguage()
        self.encrypted_text = encrypted_text
        self.all_lengths_ICs = self.get_IC_for_every_key_length()

    def symbol_in_alphabet(self, symbol: str) -> bool:
        return symbol in self.russian_language.alphabet

    def IC_counter(self, length: int) -> float:
        text = "".join([letter for letter in self.encrypted_text if self.symbol_in_alphabet(letter)])
        letters_dict = {letter: 0 for letter in self.russian_language.alphabet}
        letter_counter = 0
        for index, letter in enumerate(text):
            if index % length == 0 and self.symbol_in_alphabet(letter):
                letters_dict[letter] += 1
                letter_counter += 1

        coinced_idx = 0
        for letter in self.russian_language.alphabet:
            coinced_idx += letters_dict[letter] * (letters_dict[letter] - 1) / (letter_counter * (letter_counter - 1))

        return coinced_idx

    def get_IC_for_every_key_length(self) -> list[float]:
        ICs = {}
        for i in range(1, 101):
            ICs[i] = self.IC_counter(i)
        return ICs

class VigenereCracker:
    @dataclass
    class Crack:
        shifts: list[int]
        key: str

    def __init__(self, encrypted_text: str, key_length: int) -> None:
        self.encrypted_text = encrypted_text
        self.key_length = key_length
        self.russian_language = RussianLanguage()
        self.cracks_list = []

    def symbol_in_alphabet(self, symbol: str) -> bool:
        return symbol in self.russian_language.alphabet

    def is_valid_text(self, decrypted_text: str, limit: int, words_by_length: dict, error_rate_threshold: float) -> bool:
        words = [word.strip(string.punctuation) for word in decrypted_text.split()]

        wrong_words = 0
        total_words = 0
        for i in range(limit):
            word = self.russian_language.e_replace(words[i])
            if word not in words_by_length[len(word)]:
                wrong_words += 1
            total_words += 1
        return False if wrong_words / total_words > error_rate_threshold else True


    def build_original_text(self, shifts) -> str:
        decrypted_text = ''

        current_pos = 0
        for symbol in self.encrypted_text:
            if self.symbol_in_alphabet(symbol):
                original_order = (self.russian_language.get_order_by_letter(symbol) - shifts[current_pos % len(shifts)]) % self.russian_language.num_of_letters
                original_letter = self.russian_language.get_letter_by_order(original_order)
                decrypted_text += original_letter
                current_pos += 1
            else:
                decrypted_text += symbol

        return decrypted_text

    def count_frequencies(self) -> list[dict]:
        text = "".join([letter for letter in self.encrypted_text if self.symbol_in_alphabet(letter)])
        freqs_dicts_list = []
        for i in range(self.key_length):
            one_freq_dict = {letter: 0 for letter in self.russian_language.alphabet}
            freqs_dicts_list.append(one_freq_dict)

        for i, letter in enumerate(text):
            freqs_dicts_list[i % self.key_length][letter] += 1

        freqs_per_step = []
        for i in range(self.key_length):
            freqs_per_step.append({key: value for key, value in sorted(freqs_dicts_list[i].items(), key=lambda item: item[1])}.keys())

        return freqs_per_step

    def decrypt_text(self, limit: int, words_by_length: dict, error_threshold: float) -> dict:
        letters_frequencies = self.count_frequencies()

        for letter in letters_frequencies[0]:
            cur_crack = self.Crack(None, "")

            pos_max_freq_order = self.russian_language.get_order_by_letter(letter)
            true_max_freq_order = self.russian_language.get_order_by_letter('О') #статистически самая часто встречаемая буква русского алфавита

            shift = (pos_max_freq_order - true_max_freq_order) % self.russian_language.num_of_letters

            cur_crack.shifts = [shift]
            cur_crack.key = self.russian_language.get_letter_by_order((shift - 1) % self.russian_language.num_of_letters)

            self.cracks_list.append(cur_crack)

        while True:
            get_crack = self.cracks_list.pop()
            if len(get_crack.shifts) < self.key_length:
                for freq in letters_frequencies[len(get_crack.shifts)]:
                    cur_crack = self.Crack(None, "")

                    true_max_freq_order = self.russian_language.get_order_by_letter('О')
                    pos_max_freq_order = self.russian_language.get_order_by_letter(freq)
                    shift = (pos_max_freq_order - true_max_freq_order) % self.russian_language.num_of_letters

                    cur_crack.shifts = get_crack.shifts + [shift]
                    cur_crack.key = get_crack.key + self.russian_language.get_letter_by_order((shift - 1) % self.russian_language.num_of_letters)
                    self.cracks_list.append(cur_crack)
            else:
                decrypted_text = self.build_original_text(cur_crack.shifts)
                is_valid = self.is_valid_text(decrypted_text, limit, words_by_length, error_threshold)
                if is_valid:
                    decrypted_text_info = {'decryptedText': decrypted_text, 'shifts': cur_crack.shifts, 'key': cur_crack.key}
                    with open(f"materials/оригинал.txt", 'w+') as f:
                        f.write(decrypted_text)
                        f.write('\n')
                    with open(f"materials/ключ.txt", 'w+') as f:
                        f.write(cur_crack.key)
                        f.write('\n')
                    return decrypted_text_info