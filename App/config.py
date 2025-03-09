class Config:
    SECRET_KEY = 'B!1w8NAt1T^%kvhUI*S^'

class DevelopmentConfig(Config):
    DEBUG = True
    #MONGO_URI = "mongodb://localhost:27017/software3"
    MONGO_URI = "mongodb+srv://unix:unix@cluster0.51z20q3.mongodb.net/unilocal"

config = {
    'development': DevelopmentConfig
}