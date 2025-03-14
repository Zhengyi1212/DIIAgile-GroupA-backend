from app._init_ import create_app
from flask_cors import CORS

app = create_app()
# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:111111@localhost:3306/campus'

if __name__ == "__main__":
    app.run(debug=True)