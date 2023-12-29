from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://ask:ask@cluster0.ub2vbnc.mongodb.net/?retryWrites=true&w=majority")
db = cluster["laundry"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["get","post"])

def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:","")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        res.message("Hi, Thanks for contacting *TheLaundryMax.in*.  \nyou can choose from one of the options below: " "\n\n*Type*\n\n1️⃣ To *Contact us*\n2️⃣To *Order*\n3️⃣To know our *Working hours*\n4️⃣To get our *Address*")
        users.insert_one({"number": number, "status": "main","messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("please enter a valid response")
            return str(res)

        if option == 1:
            res.message("You can contact us through phone or e-mail.\n\n*Phone:* +91-99252525\n*e-mail:* info@laundrymax.in")
        elif option == 2:
            res.message("You have entered *Ordering mode*")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message("You can select one of the following services to order: \n\n1️⃣ *Wash & Steam Iron* \n2️⃣ *Wash & Fold* \n3️⃣ *Premium Laundry*\n4️⃣ *House holds*\n5️⃣ *Dry Cleaning*\n6️⃣ *Commercial Laundry*\n0️⃣ *Go Back*")
        elif option == 3:
            res.message("We work every day from *9AM to 9PM*")
        elif option == 4:
            res.message("We have many centres across the city.Our main center is at 301, Hafeezpet, Hyderabad")
        else:
            res.message("Please enter a valid response")
            return str(res)
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: " "\n\n*Type*\n\n1️⃣ To *Contact* us\n\n2️⃣ To *Order*\n\n3️⃣ To know our *Working hours*\n\n4️⃣ To get our *Address*")

        elif 1<= option <=9:
            lServices = ["Wash & Steam Iron","Wash & Fold","Premium Laundry","House holds","Dry Cleaning","Commercial Laundry"]
            selected = lServices[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number},{"$set":{"item": selected}})
            res.message("Excellent 😉")
            res.message("Please enter your address to confirm the order")

        else:
            res.message("Please enter a valid response")

    elif user["status"] == "address":
        selected = user["item"]

        res.message(f"You ordered for the service *{selected}*. Our customer Agent will contact you shortly!!")
        res.message("Thanks for choosing *TheLaundryMax*")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})

    elif user["status"] == "ordered":
        res.message(
            "Hi, Thanks for contacting again *TheLaundryMax.in*.  \nyou can choose from one of the options below: " "\n\n*Type*\n\n1️⃣ To *Contact* us\n\n2️⃣ To *Order*\n\n3️⃣ To know our *Working hours*\n\n4️⃣ To get our *Address*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})


    users.update_one({"number": number},{"$push": {"messages": {"text": text,"date": datetime.now()}}})

    return str(res)

if __name__ == "__main__":
    app.run()

