# -*- coding: utf-8 -*-z
from aiogram import Bot, Dispatcher, executor, types
import os
import torch
import json
import shutil
import logging
from peft import PeftModel, PeftConfig
from transformers import AutoTokenizer, T5ForConditionalGeneration, GenerationConfig, AutoModelForSeq2SeqLM

def build_jsonl(dict_list, name):
    with open(f'{name}.jsonl', 'w', encoding='utf-8') as outfile:
        for entry in dict_list:
            json.dump(entry, outfile, ensure_ascii=False)
            outfile.write('\n')

def open_jsonl(name):
    ret =[]
    with open(f'{name}.jsonl', 'r', encoding='utf-8') as json_file:
        json_list = list(json_file)
    for json_str in json_list:
        result = json.loads(json_str)
        ret.append(result)
    return(ret)


# the function for making requests to the model
def interference(req):

    generation_config = GenerationConfig.from_pretrained('SiberiaSoft/SiberianPersonaFred')

    que = "<SC6>Ты парень, программист. Ты очень умный и любишь помогать. Отвечаешь кому-то в чате DevOps. Продолжи диалог:\n"+req+"\nТы:<extra_id_0>"

    data = tokenizer(
        que,
        return_tensors='pt')
    data = {k: v.to(model.device) for k, v in data.items()}
    output_ids = model.generate(
        **data,
        generation_config=generation_config,
        max_length=1024,
    )[0]
    # print(tokenizer.decode(data["input_ids"][0].tolist()))
    answer = tokenizer.decode(output_ids.tolist())
    print(answer)
    cleared_answer = answer[answer.find('<extra_id_0>')+12:-4]
    return(cleared_answer)


logging.basicConfig(level=logging.INFO)
bot_token = '6669944175:AAEhZMZA0jcM0VduPMl9SVanUNBkceSCdzs'
bot = Bot(token=bot_token)
dp = Dispatcher(bot)


# clearing the "offload" folder (the program may work unstable if we don't do this)
if os.path.isdir('offload'):
    shutil.rmtree('offload')


# booting the model
print('booting the model...')
peft_model_path = "models/DevOpsDudeSimulacrum"
base_model_path = "models/SiberianPersona"

peft_model_base = AutoModelForSeq2SeqLM.from_pretrained(base_model_path, torch_dtype=torch.bfloat16)
tokenizer = AutoTokenizer.from_pretrained(base_model_path)
# Load the Lora model
model = PeftModel.from_pretrained(peft_model_base, peft_model_path,
                                       is_trainable=False, offload_folder="offload/")
model = model.merge_and_unload()
model = model.to('cpu')


print('model booted')


@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    history = open_jsonl('history')
    user_id = message['from']['id']
    for story in history:
        if story['user_id'] == user_id:
            history.remove(story)
    build_jsonl(history, 'history')
    await message.reply(text='Контекст очищен')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(text='Привет! Я - бот, который делает вид, что он человек из чата девопсов. '
                             'Я не проходил никаких курсов от Тинькоффа, поэтому плохо знаю, о чём говорю. '
                             'Зато делаю это очень уверенно. '
                             'Я запоминаю контекст диалога. Чтобы очистить контекст, напишите /clear')


@dp.message_handler(content_types=['text'])
async def req(message: types.Message):
    try:
        history = open_jsonl('history')
        request = message['text']
        print(request)
        user_id = message['from']['id']
        main_story = None
        for i in range(len(history)):
            story = history[i]
            if story['user_id'] == user_id:
                main_story = story
                ind = i
                break
        if main_story is None:
            ind = len(history)
            history.append({'user_id': user_id, 'dialogue': []})
            main_story = {'user_id': user_id, 'dialogue': []}

        main_story['dialogue'].append('Собеседник: ' + request)
        text = interference('\n'.join(main_story['dialogue']))

        success = 1
    except Exception as ex:
        print(ex)
        text = "Простите, не могу говорить. Бэкэнд отвалился."

        success = 0

    await message.reply(text=text)

    if success:
        main_story['dialogue'].append('Ты: ' + text)
        history[ind] = main_story

        build_jsonl(history, 'history')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
