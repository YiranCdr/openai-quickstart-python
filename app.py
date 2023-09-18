import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
system_prompt_assistant_id = os.getenv("SYSTEM_PROMPT_ASSISTANT_ID")
system_prompt_assistant_profile = os.getenv("SYSTEM_PROMPT_ASSISTANT_PROFILE")
system_prompt_assistant_chat_style = os.getenv(
    "SYSTEM_PROMPT_ASSISTANT_CHAT_STYLE")
system_prompt_user_id = os.getenv("SYSTEM_PROMPT_USER_ID")
system_prompt_user_profile = os.getenv("SYSTEM_PROMPT_USER_PROFILE")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        user_input = request.form["animal"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=generate_prompt(user_input),
            temperature=0.5,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        print(response)
        return redirect(url_for("index", result=response.choices[
            0].message.content))

    # result = request.args.get("result")
    result = generate_prompt("")
    return render_template("index.html", result=result)


def generate_prompt(user_input):
    return [
        {"role": "system", "content": system_prompt_assistant_id},
        {"role": "system", "content": system_prompt_assistant_profile},
        {"role": "system", "content": system_prompt_assistant_chat_style},
        {"role": "system", "content": system_prompt_user_id},
        {"role": "system", "content": system_prompt_user_profile},
        {"role": "user", "content": user_input},
    ]
