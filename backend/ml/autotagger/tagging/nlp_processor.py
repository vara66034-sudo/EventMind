import re
import pymorphy3
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    Doc
)

morph = pymorphy3.MorphAnalyzer()

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)

# Список слов, которые нам не нужны
FORBIDDEN_WORDS = {
    'билет', 'сайт', 'удача', 'количество', 'возможность', 'информация',
    'область', 'акция', 'кубок', 'работа', 'участие', 'формат', 'час',
    'суббота', 'воскресенье', 'апрель', 'май', 'июнь', 'июль'
}


def is_junk_entity(text: str) -> bool:
    """
    Проверяет, является ли текст нежелательной сущностью (имя, локация и т.д.)
    """
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)

    # Если Natasha нашла сущность, мы ее отсекаем
    if doc.spans:
        for span in doc.spans:
            if span.type in ['PER', 'LOC', 'ORG']:
                return True
    return False


def clean_text(text: str) -> str:
    if not text: return ""

    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    # Оставляем буквы, цифры и спецсимволы для C++ / C#
    text = re.sub(r"[^а-яА-Яa-zA-Z0-9+#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()
    lemmatized_words = []

    for word in words:
        # 1. Латиница (it, posfam) - оставляем как есть
        if re.match(r'[a-zA-Z]+', word):
            if 3 <= len(word) <= 15:
                lemmatized_words.append(word.lower())
            continue

        # 2. Обработка кириллицы
        p = morph.parse(word)[0]

        # Если в слове есть признаки имени, фамилии или отчества - в мусор
        if any(tag in p.tag for tag in ['Name', 'Patr', 'Surn', 'Geox']):
            continue

        normal = p.normal_form

        # 3. ФИЛЬТР ПО ЧАСТЯМ РЕЧИ И ДЛИНЕ
        # p.tag.animacy — проверка на одушевленность
        # 'inan' - неодушевленное (то, что нам нужно: форум, разработка)
        # 'anim' - одушевленное (то, что мы убираем: голландец, снегурочка, судья)
        if (p.tag.POS == 'NOUN' and
                p.tag.animacy == 'inan' and  # <--- Оставляем только неодушевленные
                normal not in FORBIDDEN_WORDS and
                3 <= len(normal) <= 15):

            if not is_junk_entity(word.capitalize()):
                lemmatized_words.append(normal)

    return " ".join(list(dict.fromkeys(lemmatized_words)))
