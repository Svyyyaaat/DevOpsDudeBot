# DevOpsDudeBot
telegram chatbot fine-tuned on a DevOps' chat

Code, model and dependencies **packed in a docker** (github doesn't let me upload such big files):

https://drive.google.com/file/d/1FU0SLYkjJnynO6YaFolLeLkAOeERXW6w/view?usp=drive_link

telegram bot: @DevOpsDudeBot (probably inactive rn)

# Model
The model is based on SiberiaSoft/SiberianPersonaFred, which is a FRED-T5 (russian T5) model fine-tuned for conversations. Then I PEFT fine-tuned it on data from a DevOps' telegram chat.

The base notebook used for fine-tuning:
https://www.kaggle.com/code/paultimothymooney/fine-tune-flan-t5-with-peft-lora-deeplearning-ai/notebook

I had to alter it a bit. Note that I only ran the cells related to PEFT fine-tuning and didn't ran anything related to the traditional fine-tuning. The altered version:
https://www.kaggle.com/svyatoslavakimov/fine-tune-flan-t5-with-peft-lora-deeplearning-ai

# Data
The dataset ('devops-reply-v2.jsonl' in the repo) has about 10k rows with columns 'question' and 'answer'. The 'answer' column includes reply messages, and 'question' has the messages that have been replied to. So, for example, if there were 3 messages like that:

12:00 user1: Hello
12:30 user2: I love puncakes
13:00 user3 (reply to 12:00 user1: Hello): Hi dude, how'r you doing?

Only one column would be added to the dataset:
{question: "Hello", answer: "Hi dude, how'r you doing?"} ✅

instead of:
{question: "Hello", answer: "I love puncakes"} ❌
{question: "I love puncakes", answer: "Hi dude, how'r you doing?"} ❌

It was made like that in order to reduce the amount of weird disconnected dialogues. 

# Bot
The bot is ran with the help of the aiogram library.
* Stores conversation history
* Has the function to clean history

# What can be added
The bot can reply slowly, since the model is PEFT fine-tuned. With more resources and the given notebook it is possible to train the model the classic way, making it faster and perhaps smarter about the topic it talks about.

# Why T5-based model?
Because it's light enough to run on my computer and performs better than GPT-2 based models. If I had more resources I would choose a Llama-based model, like one of the Saigas.
