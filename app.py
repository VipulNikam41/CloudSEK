from flask import Flask, render_template, request, redirect
# importing flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
# libraries to handle database

from multiprocessing import Process
import time
# libraries to handle multiprocessing while program sleeps for 10 sec.

app = Flask(__name__)

# initialize SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Sum.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)

class dataBase(db.Model):
	# creating dataBase with four columns
    sno = db.Column(db.Integer, primary_key=True) #unique_identifier
    num1 = db.Column(db.Integer, nullable=False) #first Number
    num2 = db.Column(db.Integer, nullable=False) #second Number
    addition = db.Column(db.Integer) #to store answers

    # Constructor
    def __init__(self, number1, number2, addition):
        self.num1 = number1
        self.num2 = number2
        self.addition = addition

    #to get class object in the form of string for /show api call
    def __repr__(self) -> str:
        return f"{self.sno}\t{self.num1}\t{self.num2}\t{self.addition}\n<br>"


# Home Page
@app.route("/")
def index():
	# By default Status code will be 200
    return "Hi from test API"

# to add numbers in database from url
@app.route("/calculate/<int:number1>/<int:number2>/")
def addition(number1, number2):
    p = 1 # to calculate index of current row in database
    for row in db.session.query(dataBase):
    	# iterating thorugh the database
        p += 1
        if row.num1 == number1 and row.num2 == number2:
        	# checking presence of givent entry in database
            key = row.sno
            return f"{key} is unique_identifier for given query"

    # if entrry dosnt exist already, adding it to database.
    Sum = dataBase(number1, number2, None)
    db.session.add(Sum)
    db.session.commit()

    # returning unique_identifier
    return f"{number1} and {number2} added to database with unique_identifier {p}"

# to make program sleep for 10 seconds and the calculating answer and updating in database.
def newF(instance, identifier):
	# updating answer for given instance.
    time.sleep(10)
	# heavey proses will add answer to givent database after 10 second.
    instance.addition = instance.num1 + instance.num2
    answer = instance.addition
    db.session.commit()


# to get answer for givent identifier
@app.route("/get_answer/<int:identifier>/")
def message(identifier):
	# checking wrther given identifier exist in table or not
    ex = db.session.query(exists().where(dataBase.sno == identifier)).scalar()
    if ex == False:
    	# returing 404 error if dosnt exist.
        return "Identifier entry does not exist in the database", 404

    # getting the row beloning to given instance
    instance = dataBase.query.get_or_404(identifier)
    if instance.addition == None:
		# as answer is not calculated, it will create a heavry proses
		# heavey proses will add answer to givent database after 10 second.
        heavy_process = Process(target=newF, args=(instance, identifier), daemon=True)
        heavy_process.start()
		# it will retruing please wait to the user.
        return "Please wait.(you will get answer for this query after 10 seconds)"
    else:
    	# as answer exists in database already, it will simply return its value
        ans = instance.addition
        return f"{ans}"


@app.route("/show")
def show():
    # to show database in browser
    # i.e to access data from Sum.db
    allSum = dataBase.query.all()
    return f"this is database page<br>{allSum}"


if __name__ == "__main__":
	# main function
    app.run(debug=True)