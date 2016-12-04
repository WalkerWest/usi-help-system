from main import app
from flask import render_template,flash,redirect,url_for,g,request,session,jsonify
from models import Item, UserClass, Contact, Category, Problem, Node, Tree
from forms import ItemForm, DelForm, EditForm
from threading import Lock
from google.appengine.ext import ndb
import uuid
import hashlib
import config
import ast

counter=10
catList=[]
probList=[]
roots = []

def storeCat(myCat):
    myCat2=Category(name=myCat)
    myCat2.put()
    return myCat2

def storeProb(myProb, myAns):
    if myProb==None: myProb=""
    if myAns==None: myAns=""
    myProb2=Problem(problem=myProb,solution=myAns)
    myProb2.put()
    return myProb2

@app.route('/',methods=['GET','POST'])
def index():
    global catList
    global probList
    global counter
    lock=Lock()
    with lock:
        counter+=1
        print (counter)
    if request.form.has_key("changeCat") or request.form.has_key("changeProb"):
        myObj = None
        for node in roots:
            if (node.nodeType() == "Category" and node.payload.name == request.form['selectedCat']) or node.nodeType() == "Problem":
                myObj = node
                break
        if myObj!=None:
            del roots[:]
            for thing in myObj.returnRootChildren():
                roots.append(thing)
    # return render_template("wwindex.html",roots=roots)
    return redirect("static/wwindex.html")

@app.route('/_getUser')
def get_user():
    return jsonify({'user':session['username']})

@app.route('/_getTrees')
def get_tree():
    returnList=[]
    for tree in roots:
        returnDict = {}
        returnDict['id']=tree.payload.id
        returnDict['name']=tree.payload.name
        returnList.append(returnDict)
    return jsonify(returnList)

@app.route('/_getChildren')
def get_children():
    returnList=[]
    myNode=None
    for category in catList:
        if str(request.args.get("id"))==str(category.id):
            myNode=category
            print "Found category "+category.name
            break
    baseNode=None
    for tree in roots:
        baseNode=tree.lookup(request.args.get("id"))
        if baseNode!=None: break
    if baseNode!=None:
        for node in baseNode.returnRootChildren():
            returnDict = {}
            returnDict['id']=node.payload.id
            if hasattr(node.payload,'name'):
                returnDict['name']=node.payload.name
                returnDict['type']="category"
            elif hasattr(node.payload,'problem') and node.payload.problem!=None:
                returnDict['name'] = node.payload.problem
                returnDict['type']="problem"
            elif hasattr(node.payload,'solution') and node.payload.solution!=None:
                returnDict['name'] = node.payload.solution
                returnDict['type']="solution"
            returnList.append(returnDict)
    return jsonify(returnList)

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submittedContacts', methods=['POST'])
def submitted_form():
    #Get info from fields
    name = request.form['name']
    email = request.form['email']
    comments = request.form['comments']
    #use Contact constructor to make db item
    contactObj=Contact(name=request.form['name'],
                 email=request.form['email'],
                 comments=request.form['comments'])
    #Store obj in database
    contactObj.put()
    return render_template(
        'submittedContacts.html',
        name=name,
        email=email,
        comments=comments)

@app.route('/logout')
def logout():
    #Clear session data to log out
    session.clear()
    return render_template('logout.html')

#User inputs username/password
@app.route('/login')
def login():
    return render_template('login.html')

#app takes username/password and authenticates user
@app.route('/authenticate', methods=['POST'])
def authenticate():
    userexists=False
    #Get username and password from login form
    username=request.form['username']
    password=request.form['password']
    #Hash password for comparison with hash entry in database
    h = hashlib.md5()
    h.update(password)
    hashpassword = h.hexdigest()
    #Print to console for troubleshooting
    #print(username)
    #print(hashpassword)
    #Get list of usuers
    users=UserClass.query()
    #Compare username from form with every username in database
    for user in users:
        #print(user.username)
        #If username found, set userexists true
        if user.username==username:
            userexists=True
            #print(hashpassword)
            # If username found, check password from form with password in databse for that username
            if user.password==hashpassword:
                #Set session data with username
                session['username'] = username
                flash('Logged in successfully.')
                return render_template('authenticated.html')
    #If login failed, tell user either username or password was bad, return to login form
    flash('Login failed');
    if userexists==False: flash('Username does not exist')
    else: flash('Incorrect password')
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/registersubmitted', methods=['POST']) #https://docs.python.org/2/library/hashlib.html
def registersub():
    print("got in")
    #get info from fields
    username = request.form['username']
    print("thats one")
    email = request.form['email']
    print("thats two")
    #get password from field, create md5 hash for more secure storage
    password = request.form['password']
    h = hashlib.md5()
    h.update(password)
    passwordhash=h.hexdigest()
    print(passwordhash)
    print("got info")
    #build user object
    userObj = UserClass(username = request.form['username'],
                        email = request.form['email'],
                        password = passwordhash,
                        rights='1')
    print("built obj")
    #Store user in db
    userObj.put()
    print("stored obj")
    return render_template('registersubmitted.html',
                            username=username)

def setupTree():
    if len(roots) == 0:
        metaData = Tree.query()
        if len(metaData.fetch(None)) == 0:
            r1 = Node(storeCat("Lawn Equipment"))
            roots.append(r1)
            lm = r1.addSubNode(storeCat("Lawn Mower"))
            we = r1.addSubNode(storeCat("Weed Eater"))
            r1.addSubNode(storeCat("Edger"))

            r2 = Node(storeCat("Mobile Phone"))
            rr2 = r2.addSubNode(storeProb("Are you having a problem?", None))
            roots.append(r2);
            gp = rr2.addSubNode(storeProb("Does the lawn mower have gas?", None))
            rr2.addSubNode(storeProb("Is the lawn mower making noises?", None))
            gp.addSubNode(storeProb(None, "You don't have any gas!"))

            we.addSubNode(storeCat("Torro"))
            honda = lm.addSubNode(storeCat("Honda"))
            bd = lm.addSubNode(storeCat("B&D"))
            honda.addSubNode(storeProb("WOW", None))
            bd.addSubNode(storeCat("itWORKS!"))

            r1.printTree()
            r2.printTree()
            treeDict = r1.convertTree()
            Tree(tree=str(r1.convertTree())).put()
            Tree(tree=str(r2.convertTree())).put()
            r1Prime = Node(treeDict)
            print r1
            print r1Prime
            r1Prime.printTree()
        else:
            for probsol in Problem.query(): probList.append(probsol)
            for cat in Category.query(): catList.append(cat)
            trees = Tree.query()  # get item list
            for tree in trees:  # find correct item
                roots.append(Node(ast.literal_eval(tree.tree)))
            print "Length of probList is " + str(len(probList))
            print "Length of catList is " + str(len(catList))