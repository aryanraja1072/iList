#!flask/bin/python
from flask import  Flask,jsonify,make_response,abort,request
import sqlite3
from sqlite3 import Error


class TaskDB:
    def __init__(self):
        self.conn = sqlite3.connect('iList.db',check_same_thread=False)
        print('Database Connected Successfully')
        self.cursor = self.conn.cursor()

    def createTables(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS user(userid INTEGER PRIMARY KEY,username TEXT UNIQUE, pwd_hash TEXT);''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS category(ctgid INTEGER PRIMARY KEY,title TEXT,userid INTEGER, FOREIGN KEY(userid) REFERENCES user(userid) ON DELETE CASCADE,UNIQUE(title,userid));''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS item(itemid INTEGER PRIMARY KEY,task TEXT,done INTEGER, ctgid INTEGER,FOREIGN KEY(ctgid) REFERENCES category(ctgid) ON DELETE CASCADE,UNIQUE(task,ctgid)); ''')
            self.conn.commit()
        except Error as e:
            return ("Create Table status:ERROR ->",e)
        return "Create Table status:OK"
    def insertUser(self,username,pwd_hashed):
        try:
            self.cursor.execute('''INSERT INTO user(username,pwd_hash) values(?,?);''',(username,pwd_hashed))
            self.conn.commit()
        except Error as e:
            return ("Insert 'user' status:ERROR ->",e)
        return "Insert 'user' status:OK"
    def insertCategory(self,title,userid):
        try:
            self.cursor.execute('''INSERT INTO category(title,userid) values(?,?);''',(title,userid))
            self.conn.commit()
        except Error as e:
            return ("Insert 'category' status:ERROR ->",e)
        return "Insert 'category' status:OK"
    
    def insertItem(self,task,done,ctgid):
        try:
            self.cursor.execute('''INSERT INTO item(task,done,ctgid) values(?,?,?);''',(task,done,ctgid))
            self.conn.commit()
        except Error as e:
            print("Insert 'item' status:ERROR ->",e)  
            return ("Insert 'item' status:ERROR ->",e)
        return "Insert 'item' status:OK"
    def getUsers(self):
        users=[]
        try:
            self.cursor.execute("SELECT * from user;")
            userTuples = self.cursor.fetchall();
            for user in userTuples:
                print(user)
                userDict={
                    'userid':user[0],
                    'username':user[1],
                    'pwd_hash':user[2]
                }
                users.append(userDict)
        except Error as e:     
            print("SELECT 'users' status:ERROR -> ",e)
        finally:

            return users

    def getCategories(self,userid):
        categories=[]
        try:
            self.cursor.execute('''SELECT * FROM category WHERE userid = ?;''',(userid,))
            categoryTuples=self.cursor.fetchall();
            for category in categoryTuples:
                categoryDict ={'ctgid':category[0],
                            'title':category[1],
                            'userid':category[2]}
                categories.append(categoryDict)

        except Error as e:     
            print("SELECT 'category' status:ERROR -> ",e)
        finally:
            return categories

    def getItems(self,ctgid):
        items=[]
        try:
            self.cursor.execute('''SELECT * FROM item WHERE ctgid = ?;''',(ctgid,))
            itemTuples=self.cursor.fetchall();
            for item in itemTuples:
                itemDict ={'itemid':item[0],
                            'task':item[1],
                            'done':item[2],
                            'ctgid':item[3]}
                items.append(itemDict)

        except Error as e:     
            print("SELECT 'category' status:ERROR ->",e)
        finally:
            return items

    def verifyUser(self,userid,pwd_hash):
        pwd=None
        try:
            self.cursor.execute("SELECT pwd_hash from user where userid=?;",(userid,))
            pwd=self.cursor.fetchone()[0]
        except Error as e:
            print('verifyUser Method:ERROR ->',e)
        finally:
            if pwd == None or pwd != pwd_hash:
                return False
            return True
    def doesUserExists(self,username):
        count = 0
        try:
            self.cursor.execute("SELECT COUNT(userid) from user where username=?;",(username,))
            count = self.cursor.fetchone()[0]
        except Error as e:
            print('doesUserExists Method:ERROR ->',e)
        finally:
            if count == 0:
                return False
            return True
    def getUserID(self,username):
        userid = -1
        try:
            self.cursor.execute("SELECT userid from user where username=?;",(username,))
            userid = self.cursor.fetchone()[0]
        except Error as e:
            print('getUserID Method:ERROR ->',e)
        finally:
            return userid
    
app = Flask(__name__)


@app.route('/iList/api/v1.0/users',methods=['GET'])
def getUsers():
    db = TaskDB()
    users=db.getUsers()
    if len(users) == 0:
        abort(404)
    return jsonify({'users':users})
@app.route('/iList/api/v1.0/categories',methods=['GET'])
def get_Catgs():
    db = TaskDB()
    userid = int(request.args.get('userid'))
    pwd_hash = request.args.get('pwd_hash')
    if not db.verifyUser(userid,pwd_hash):
        return make_response(jsonify({'error':'Unauthorized access'}),401)
    catgs = db.getCategories(userid)
    if len(catgs) == 0:
         abort(404)
    return jsonify({'categories':catgs})

@app.route('/iList/api/v1.0/items',methods=['GET'])
def getItems():
    db = TaskDB()
    ctgid = int(request.args.get('ctgid'))
    userid = int(request.args.get('userid'))
    pwd_hash = request.args.get('pwd_hash')
    if not db.verifyUser(userid,pwd_hash):
        return make_response(jsonify({'error':'Unauthorized access'}),401)
    items = db.getItems(ctgid)
    print(items)
    return jsonify({'items':items})

@app.route('/iList/api/v1.0/items/add',methods=['GET'])
def insertItem():
    db = TaskDB()
    ctgid = int(request.args.get('ctgid'))
    userid = int(request.args.get('userid'))
    pwd_hash = request.args.get('pwd_hash')
    if not db.verifyUser(userid,pwd_hash):
        return make_response(jsonify({'error':'Unauthorized access'}),401)
    task = request.args.get('task');
    done = int(request.args.get('done'))
    if done == None:
        done = 0
    db.insertItem(task,done,ctgid)
    items = db.getItems(ctgid)
    return jsonify({'items':items})

    

#@app.route('/iList/api/v1.0/users/add/<string:username>/<string:pwd_hash>',methods=['GET'])
@app.route('/iList/api/v1.0/users/add',methods=['GET'])
def addUser():
    db = TaskDB();
    username=request.args.get('username')
    pwd_hash=reques.args.get('pwd_hash')
    if not db.doesUserExists(username):
        db.insertUser(username,pwd_hash)
        return make_response(jsonify({'userid':db.getUserID(username)}),201)
    else:
        return make_response(jsonify({'error':'Username already registered'}),409)



if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
    #app.run(debug=True)
