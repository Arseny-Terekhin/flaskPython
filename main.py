from flask import Flask, render_template, request, redirect

app = Flask(__name__)
dict = {}


@app.route("/base", methods=['POST', 'GET'])
def insert():
    if request.method == 'POST':
        dict[request.form['name']] = request.form['str']
        return redirect('/base')
    else:
        return render_template("view.html", dict=dict)


@app.route("/base/delete/<string:key>")
def delete(key):
    del dict[key]
    return redirect('/base')


@app.route("/base/<string:key>/<string:value>", methods=['POST', 'GET'])
def update(key, value):
    if request.method == 'POST':
        dict[request.form['name']] = request.form['str']
        return redirect('/base')
    else:
        return render_template("view.html", dict=dict, key=key, value=value)


if __name__ == "__main__":
    app.run(debug= True)