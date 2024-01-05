## importing all dependencies
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import spacy
# make sure to have spacy english nlp model downloaded if not run "python -m spacy download en_core_web_sm" to download
import codecs
from textblob import TextBlob as tb

## setting input variable to the location of input File provided in EXCEL format
input_filepath = "./files/Input.xlsx"
## reading excel files using pandas in to a dataframe
df = pd.read_excel(input_filepath)
nlp = spacy.load("en_core_web_sm")  # Load the English NLP model

##  make a function that scrapes given url and saves that perticular url's content in a text file on the system.
def scrap_url(url):
    try:
        res = requests.get(url)
        res.raise_for_status()  # Raise an exception for non-200 status codes

        html = res.text
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("h1", class_="entry-title")
        if title:
            title = title.text.strip()

        content_div = soup.find("div", class_="td-post-content") or soup.find("div", class_="td-main-content")
        if not content_div:
            page = soup.find("div", class_="wpb_wrapper")
            if page:
                title = page.find("h1", class_="tdb-title-text")
                if title:
                    title = title.text.strip()
                content_div = page.find("div", class_="tdb-block-inner")

        paragraphs = ""
        if content_div:
            for pre in content_div.find_all("pre"):  # Remove all <pre> tags
                pre.decompose()
            paragraphs = content_div.get_text(separator=" ", strip=True)

        if title and paragraphs:
            url_id = df["URL_ID"][row]
            print(url_id)
            with open(url_id, "w") as tosave:
                tosave.write(title + " " + paragraphs)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {url} ({e})")
    except Exception as e:
        print(f"Unexpected error: {e}")

for row in range(len(df)):
    url = df.at[row, 'URL']
    scrap_url(url)

## a function to get all stop words provided along the assignment in python list
def get_stop_words():
    stop_words = []
    filenames = ["StopWords_Auditor.txt", "StopWords_Currencies.txt", "StopWords_DatesandNumbers.txt", "StopWords_GenericLong.txt", "StopWords_Generic.txt", "StopWords_Geographic.txt", "StopWords_Names.txt"]
    for filename in filenames:
        try:
            with open(f"./files/StopWords/{filename}", "r") as file:
                contents = file.read()
                if "|" in contents:
                    stop_words.append(contents.lower().replace("|","\n") .split(sep="\n"))
                else:
                    stop_words.append(contents.lower().split(sep="\n"))
        except UnicodeDecodeError:
            with open(f"./files/StopWords/{filename}", "r", encoding="iso-8859-1") as file:
                contents = file.read()
                if "|" in contents:
                    stop_words.append(contents.lower().replace("|","\n") .split(sep="\n"))
                else:
                    stop_words.append(contents.lower().split(sep="\n"))
    flat_list = sum(stop_words, [])
    flat_list = [item.strip() for item in flat_list]
    return flat_list
stop_words = get_stop_words()

## a function to get all negative words provided along the assignment in python list
def get_negative_words():
    negative_words = []
    with open("./files/MasterDictionary/negative-words.txt","r", encoding="cp1252") as temp:
        t = temp.read()
        negative_words = t.splitlines()
        negative_words = [item.strip() for item in negative_words]
    return negative_words

negative_words  = get_negative_words()

## a function to get all postive words provided along the assignment in python list

def get_positive_words():
    positive_words = []
    with open("./files/MasterDictionary/positive-words.txt","r") as temp:
        t = temp.read()
        positive_words = t.splitlines()
        positive_words = [item.strip() for item in positive_words]
    return positive_words

positive_words  = get_positive_words()

new_negatives = []
new_positives = []

for element in negative_words:
    if element not in stop_words:
        new_negatives.append(element)

for element in positive_words:
    if element not in stop_words:
        new_positives.append(element)

## get the paragraphs text from the sraped text file with "url_id" as name
def get_scrapped_paragraphs(row):
    paragraphs = ""
    url_id = df.at[row, "URL_ID"] 
    try:
        with open(f"./{url_id}","r") as file:
           paragraphs = file.read()
    except FileNotFoundError:
        pass
    return paragraphs
def func_positive_score(texts):
    return sum(word in texts.lower().split() for word in new_positives)


def func_negative_score(texts):
    return sum(word in texts.lower().split() for word in new_negatives)


def func_polarity_score(texts):
    texts = tb(texts)
    return texts.sentiment[0]


def func_subjectivity_score(texts):
    texts = tb(texts)
    return texts.sentiment[1]


def func_avg_sentence_length(texts):
  sentences = texts.sentences
  total_words = sum(len(sentence.words) for sentence in sentences)
  return total_words / len(sentences) if len(sentences) else 0


def func_count_syllables(word):
  vowels = "aeiouy"
  word = word.lower()
  syllable_count = 0
  for i in range(len(word)):
      if word[i] in vowels:
          syllable_count += 1
          if i != len(word) - 1 and word[i + 1] in vowels and word[i] != "e":
              syllable_count -= 1
  return syllable_count


def func_complex_word_percentage(texts):
  words = texts.words
  total_words = len(words)
  complex_words = sum(func_count_syllables(word) >= 3 for word in words)
  return (complex_words / (total_words)) * 100


def func_fog_index(texts):
  avg_sentence_len = func_avg_sentence_length(texts)
  percentage_complex_words = func_complex_word_percentage(texts)
  return 0.4 * (avg_sentence_len + percentage_complex_words)


def func_avg_words_per_sentence(text):
  sentences = texts.sentences
  return sum(len(sentence.words) for sentence in sentences) / len(sentences) if len(sentences) else 0


def func_complex_word_count(texts):
  words = texts.words
  return sum(func_count_syllables(word) >= 3 for word in words)


def func_word_count(texts):
  return len(texts.words)


def func_syllable_per_word(texts):
  words = texts.words
  total_syllables = sum(func_count_syllables(word) for word in words)
  return total_syllables / len(words) if len(words) else 0


def func_avg_word_length(texts):
  words = texts.words
  return (sum(len(word) for word in words)) / len(words) if len(words) else 0


def func_personal_pronouns(texts):
    doc = nlp(texts)
    personal_pronouns = ["I", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "myself", "yourself", "himself", "herself", "ourselves", "yourselves", "themselves"]
    pronoun_count = 0
    for token in doc:
        if token.text.lower() in personal_pronouns and not token.ent_type_:  # Check for personal pronoun and no named entity
            pronoun_count += 1
    return pronoun_count
output_filepath = "./output.xlsx"
ouput_df = pd.read_excel(output_filepath)
columns = list(ouput_df.columns)
for row in range(len(df)):
    paragraphs = get_scrapped_paragraphs(row)
    if paragraphs:
        print(f"calculating scores for {df['URL_ID'][row]} :")
        paras = " ".join(word for word in paragraphs.split() if word not in stop_words)
        texts = tb(paragraphs)
        positive_score = func_positive_score(paras)
        negative_score = func_negative_score(paras)
        polarity = func_polarity_score(paras)
        subjectivity = func_subjectivity_score(paras)
        avg_sentence_length = func_avg_sentence_length(texts)
        syllable_count = func_count_syllables(texts)
        complex_word_percentage = func_complex_word_percentage(texts)
        avg_word_length = func_avg_word_length(texts)
        personal_pronouns = func_personal_pronouns(paragraphs)
        syllable_per_word = func_syllable_per_word(texts)
        word_count = func_word_count(texts)
        complex_word_count = func_complex_word_count(texts)
        avg_words_per_sentence = func_avg_words_per_sentence(texts)
        fog_index = func_fog_index(texts)
        scores_dict = {'URL_ID': ouput_df['URL_ID'][row] , 'URL': ouput_df['URL'][row], 'POSITIVE SCORE': positive_score, 'NEGATIVE SCORE': negative_score, 'POLARITY SCORE': polarity, 'SUBJECTIVITY SCORE': subjectivity, 'AVG SENTENCE LENGTH': avg_sentence_length, 'PERCENTAGE OF COMPLEX WORDS': complex_word_percentage , 'FOG INDEX':fog_index , 'AVG NUMBER OF WORDS PER SENTENCE':avg_words_per_sentence , 'COMPLEX WORD COUNT':complex_word_count , 'WORD COUNT':word_count , 'SYLLABLE PER WORD':syllable_per_word , 'PERSONAL PRONOUNS':personal_pronouns , 'AVG WORD LENGTH': avg_word_length}
        for key,value in scores_dict.items():
            ouput_df.at[row, key] = value
try:
    with pd.ExcelWriter('my_output.xlsx') as writer:
        ouput_df.to_excel(writer,sheet_name='Sheet1')
except Exception as e:
    raise e
