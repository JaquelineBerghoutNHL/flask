from flask import Flask, render_template, request, g
from database import get_db, close_connection, init_db, insert_submission, get_submissions

app = Flask(__name__)

# Register teardown for closing database connections
@app.teardown_appcontext
def teardown_db(exception):
    close_connection(exception)

@app.route("/build_pyramid", methods=["GET"])
def build_pyramid():
    name = request.args.get("name")
    height = request.args.get("height")

    if not name or not height:
        return "<p style='color: red;'>Both 'name' and 'height' parameters are required in the URL.</p>", 400

    try:
        height = int(height)
        if 1 <= height <= 8:
            pyramid = generate_pyramid(height)
            insert_submission(name, height, pyramid)
            return f"""
            <h1>Pyramid Builder</h1>
            <h2>Hello, {name}!</h2>
            <p>Here is your pyramid of height {height}:</p>
            <pre style="font-family: monospace; line-height: 1.5;">{pyramid}</pre>
            <p><a href="/">Go back to the main page</a></p>
            """
        else:
            return "<p style='color: red;'>Height must be between 1 and 8.</p>", 400
    except ValueError:
        return "<p style='color: red;'>Height must be a valid integer.</p>", 400



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        height = request.form.get("height")
        try:
            height = int(height)
            if 1 <= height <= 8:
                pyramid = generate_pyramid(height)
                insert_submission(name, height, pyramid)
                return render_template("index.html", pyramid=pyramid, name=name, submissions=get_submissions())
            else:
                error = "Height must be a number between 1 and 8."
                return render_template("index.html", error=error, submissions=get_submissions())
        except ValueError:
            error = "Invalid input. Please enter a valid number."
            return render_template("index.html", error=error, submissions=get_submissions())
    return render_template("index.html", submissions=get_submissions())

def generate_pyramid(height):
    pyramid = []
    for i in range(1, height + 1):
        spaces = " " * (height - i)
        hashes = "#" * i
        pyramid.append(f"{spaces}{hashes}  {hashes}")
    return "<br>".join(pyramid)

if __name__ == "__main__":
    with app.app_context():
        init_db()  # Initialize the database on app start
    app.run(debug=True)
