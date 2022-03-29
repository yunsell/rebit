import os
import re
from silence_tensorflow import silence_tensorflow
from collections import OrderedDict
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from GPTserver.finetunnedModel.gptModel import TFGPT2Classifier, vocab, tokenizer
# from service.finetuning_model.preprocessing import Preprocessor

silence_tensorflow()
SENT_MAX_LEN = 39

def clean_text(sent):
    sent_clean = re.sub("[^가-힣ㄱ-ㅎㅏ-ㅣ\\s]", "", sent)
    return sent_clean

def translateTextToToken(text):
    test_data_sents = []
    test_tokenized_text = vocab[tokenizer(clean_text(text))]

    tokens = [vocab[vocab.bos_token]]
    tokens += pad_sequences([test_tokenized_text],
                            SENT_MAX_LEN,
                            value=vocab[vocab.padding_token],
                            padding='post').tolist()[0]
    tokens += [vocab[vocab.eos_token]]

    test_data_sents.append(tokens)
    return test_data_sents

def translateListToToken(List):
    data_sents = []
    for train_sent in List:
        train_tokenized_text = vocab[tokenizer(clean_text(train_sent))]

        tokens = [vocab[vocab.bos_token]]
        tokens += pad_sequences([train_tokenized_text],
                                SENT_MAX_LEN,
                                value=vocab[vocab.padding_token],
                                padding='post').tolist()[0]
        tokens += [vocab[vocab.eos_token]]

        data_sents.append(tokens)

    return data_sents

def posneg_sentiment(text):
    result = {}

    BASE_MODEL_PATH = './GPTserver/finetunnedModel/detailed_classification_model/gpt_ckpt'
    weightPath = './GPTserver/finetunnedModel/classification_model/weights/'
    new_model = TFGPT2Classifier(dir_path=BASE_MODEL_PATH, num_class=2)

    new_model.load_weights(weightPath)

    probability_model = tf.keras.Sequential([new_model, tf.keras.layers.Softmax()]) #predict 함수

    if isinstance(text, str):   # 한 문장인 경우
        token_list = translateTextToToken(text)

        predictions = probability_model.predict(token_list, batch_size=1024)

        result['pos'] = predictions[0][1]
        result['neg'] = predictions[0][0]

        return result
    else:                       # 문장 리스트인 경우
        list_result = {}
        token_list = translateListToToken(text)

        predictions = probability_model.predict(token_list, batch_size=1024)

        list_result['pos'] = predictions[0][1]
        list_result['neg'] = predictions[0][0]

        return list_result


def detailed_sentiment(text):
    BASE_MODEL_PATH = './GPTserver/finetunnedModel/detailed_classification_model/gpt_ckpt'
    weightPath = './GPTserver/finetunnedModel/detailed_classification_model/weights/'
    new_model = TFGPT2Classifier(dir_path=BASE_MODEL_PATH, num_class=6)

    new_model.load_weights(weightPath)

    if isinstance(text, str):  # 한 문장인 경우
        token_list = translateTextToToken(text)
    elif isinstance(text, list):  # 문장 리스트인 경우
        token_list = translateListToToken(text)

    result = new_model.predict(token_list, batch_size=1024)

    # label : 기쁨 : 0, 불안 : 1, 당황 : 2, 슬픔 : 3, 분노 : 4, 상처 : 5
    value = tf.argmax(result, 1)

    return result, tf.keras.backend.eval(value)

def repu_main(text):
    result = posneg_sentiment(text)
    detail, value = detailed_sentiment(text)
    data_convert = {k: round(float(v), 3) for k, v in result.items()}

    newRepu = {}

    newRepu['기쁨'] = round(float(detail[0][0]), 3)
    newRepu['불안'] = round(float(detail[0][1]), 3)
    newRepu['당황'] = round(float(detail[0][2]), 3)
    newRepu['슬픔'] = round(float(detail[0][3]), 3)
    newRepu['분노'] = round(float(detail[0][4]), 3)
    newRepu['상처'] = round(float(detail[0][5]), 3)

    detailRepu = OrderedDict(sorted(newRepu.items(), key=lambda t:t[1], reverse=True))

    data_convert['repu'] = detailRepu

    print(data_convert)

    return data_convert