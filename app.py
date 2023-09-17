import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
system_prompt = os.getenv("SYSTEM_PROMPT")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        user_input = request.form["animal"]
        response = openai.ChatCompletion.create(
            model="gpt-4-32k",
            message=generate_prompt(user_input),
            temperature=0.5,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        print(response)
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)

def generate_prompt(user_input):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
