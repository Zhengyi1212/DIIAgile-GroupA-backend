from app._init_ import create_app
from flask_cors import CORS

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)