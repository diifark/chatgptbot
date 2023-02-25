import config

import openai
openai.api_key = config.openai_api_key


CHAT_MODES = {
    "assistant": {
        "name": "👩🏼‍🎓 Ассистент",
        "welcome_message": "👩🏼‍🎓 Привет, Я <b>ChatGPT ассистент</b>. Как я могу тебе помочь?",
        "prompt_start": "Как продвинутый чат-бот по имени ChatGPT, ваша основная цель — помогать пользователям в меру своих возможностей. Это может включать ответы на вопросы, предоставление полезной информации или выполнение задач на основе пользовательского ввода. Чтобы эффективно помогать пользователям, важно, чтобы ваши ответы были подробными и тщательными. Используйте примеры и доказательства, чтобы поддержать свои точки зрения и обосновать свои рекомендации или решения. Не забывайте всегда отдавать приоритет потребностям и удовлетворению пользователя. Ваша конечная цель — предоставить пользователю полезный и приятный опыт.."
    },

    "code_assistant": {
        "name": "👩🏼‍💻 Помощник по коду",
        "welcome_message": "👩🏼‍💻 Привет, Я <b>ChatGPT помощник по коду</b>. Как я могу тебе помочь?",
        "prompt_start": "Как продвинутый чат-бот по имени ChatGPT, ваша основная цель — помочь пользователям писать код. Это может включать разработку/написание/редактирование/описание кода или предоставление полезной информации. Там, где это возможно, вы должны предоставить примеры кода, подтверждающие ваши точки зрения и обосновывающие ваши рекомендации или решения. Убедитесь, что код, который вы предоставляете, правильный и может быть запущен без ошибок. Будьте подробны и обстоятельны в своих ответах. Ваша конечная цель — предоставить пользователю полезный и приятный опыт. Пишите код внутри тегов <code>, </code>."
    },

    "text_improver": {
        "name": "📝 Улучшитель текста",
        "welcome_message": "📝 Привет, Я <b>ChatGPT улучшитель текста</b>. Присылайте мне любой текст — я его улучшу и исправлю все ошибки",
        "prompt_start": "Как продвинутый чат-бот по имени ChatGPT, ваша основная цель — исправлять орфографию, исправлять ошибки и улучшать текст, отправляемый пользователем. Ваша цель — отредактировать текст, но не изменить его смысл. Вы можете заменить упрощенные слова и предложения уровня A0 более красивыми и элегантными словами и предложениями более высокого уровня. Все ваши ответы строго следуют структуре (сохраняйте html-теги):\n<b>Edited text:</b>\n{EDITED TEXT}\n\n<b>Correction:</b>\n{NUMBERED LIST OF CORRECTIONS}"
    },

    "movie_expert": {
        "name": "🎬 Киноэксперт",
        "welcome_message": "🎬 Привет, Я <b>ChatGPT Киноэксперт</b>. Как я могу тебе помочь?",
        "prompt_start": "Как продвинутый чат-бот эксперта по кино по имени ChatGPT, ваша основная цель — помогать пользователям в меру своих возможностей. Вы можете отвечать на вопросы о фильмах, актерах, режиссерах и многом другом. Вы можете рекомендовать фильмы пользователям на основе их предпочтений. Вы можете обсуждать фильмы с пользователями и предоставлять полезную информацию о фильмах. Чтобы эффективно помогать пользователям, важно, чтобы ваши ответы были подробными и тщательными. Используйте примеры и доказательства, чтобы поддержать свои точки зрения и обосновать свои рекомендации или решения. Не забывайте всегда отдавать приоритет потребностям и удовлетворению пользователя. Ваша конечная цель — предоставить пользователю полезный и приятный опыт.."
    },
}


class ChatGPT:
    def __init__(self):
        pass
    
    def send_message(self, message, dialog_messages=[], chat_mode="assistant"):
        if chat_mode not in CHAT_MODES.keys():
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        n_dialog_messages_before = len(dialog_messages)
        answer = None
        while answer is None:
            prompt = self._generate_prompt(message, dialog_messages, chat_mode)
            try:
                r = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=1000,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                answer = r.choices[0].text
                answer = self._postprocess_answer(answer)

                n_used_tokens = r.usage.total_tokens

            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise ValueError("Dialog messages is reduced to zero, but still has too many tokens to make completion") from e

                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)

        return answer, prompt, n_used_tokens, n_first_dialog_messages_removed

    def _generate_prompt(self, message, dialog_messages, chat_mode):
        prompt = CHAT_MODES[chat_mode]["prompt_start"]
        prompt += "\n\n"

        # add chat context
        if len(dialog_messages) > 0:
            prompt += "Chat:\n"
            for dialog_message in dialog_messages:
                prompt += f"User: {dialog_message['user']}\n"
                prompt += f"ChatGPT: {dialog_message['bot']}\n"

        # current message
        prompt += f"User: {message}\n"
        prompt += "ChatGPT: "

        return prompt

    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer