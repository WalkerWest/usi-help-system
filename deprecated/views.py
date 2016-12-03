from main import app,counter
from flask import render_template,flash,redirect,url_for,g,request,session
from models import Item, UserClass, Contact, Category, Problem, Node, Tree
from forms import ItemForm, DelForm, EditForm
from threading import Lock
from google.appengine.ext import ndb
import uuid
import hashlib
import config
import ast

counter=10

@app.route('/testTree',methods=['GET','POST'])
def test():
    addForm=ItemForm()
    delForm = DelForm()
    editForm = EditForm()
    itemsOfInterest = Item.query()
    #makes database if it doesn't exist...
    if len(itemsOfInterest.fetch(None))==0:
        mower=Item(id=str(uuid.uuid1()), item='Lawn Mower')
        eater=Item(id=str(uuid.uuid1()),item='Weed Eater')
        mower.addModel('Honda')
        mower.addModel('Black & Decker')
        eater.addModel('Torro')
        eater.addModel('Echo')
        print mower.item
        print eater.item
        mower.put()
        eater.put()
        itemsOfInterest = Item.query()
    print "The query length is "+str(len(itemsOfInterest.fetch(None)))
    if request.form.has_key("edit") and editForm.validate_on_submit():  # If edit button press & something in edit box then...
        myItems = Item.query()  # get item list
        for item in myItems:  # find correct item
            print item
            print item.id
            if str(item.id) == str(editForm.id.data):
                # Get item
                item = item.key.get()
                # Change item to edit box data
                item.item = editForm.editItem.data
                # Save item
                item.put()
        flash('Item Edited!')
        return redirect(url_for('index'))
    elif request.form.has_key("delete") and delForm.validate_on_submit():
        myItems = Item.query()
        for item in myItems:
            print item
            print item.id
            if str(item.id) == str(delForm.id.data):
                ndb.delete_multi([item.key])
        flash('Item deleted!')
        return redirect(url_for('index'))
    elif request.form.has_key("add") and addForm.validate_on_submit():
        newItem = Item(id=str(uuid.uuid1()),item=addForm.item.data)
        print("myUUID is "+newItem.id)
        newItem.put()
        flash('New item added!')
        return redirect(url_for('index'))
    return render_template('index.html',
                           title='USI Help System',
                           itemsOfInterest=itemsOfInterest,
                           addForm=addForm,
                           delForm=delForm,
                           editForm=editForm
                           )

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

roots = []

def storeCat(myCat):
    myCat2=Category(myCat)
    myCat2.put()
    return myCat2

def storeProb(myProb, myAns):
    myProb2=Problem(myProb,myAns)
    myProb2.put()
    return myProb2

@app.route('/',methods=['GET','POST'])
def index():
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
    #else
    elif len(roots) == 0:
        metaData=Tree.query()
        if len(metaData.fetch(None))==0:
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
            honda.addSubNode(storeProb("WOW",None))
            bd.addSubNode(storeCat("itWORKS!"))
            r1.printTree()

            treeDict = r1.convertTree()
            Tree(str(r1.convertTree())).put()
            Tree(str(r2.convertTree())).put()
            r1Prime = Node(treeDict)
            r1Prime.printTree()
        else:
            for probsol in Problem.query(): config.probList.append(probsol)
            for cat in Category.query(): config.catList.append(cat)
            trees = Tree.query()  # get item list
            for tree in trees:  # find correct item
                roots.append(Node(ast.literal_eval(tree.tree)))



    return render_template("testindex.html",
                           roots=roots)


@app.route('/wwTest')
def index2():
    global counter
    lock=Lock()
    with lock:
        counter+=1
        print (counter)

@app.route('/wwRoot',methods=['GET','POST'])
def wwIndex():
    global counter
    lock=Lock()
    with lock:
        counter+=1
        print (counter)
    form=ItemForm()
    itemsOfInterest = Item.query()
    if len(itemsOfInterest.fetch(None))==0:
        mower=Item(id=str(uuid.uuid1()), item='Lawn Mowers')
        eater=Item(id=str(uuid.uuid1()),item='Weed Eaters')
        mower.addModel('Honda')
        mower.addModel('Black & Decker')
        eater.addModel('Torro')
        eater.addModel('Echo')
        print mower.item
        print eater.item
        mower.put()
        eater.put()
        itemsOfInterest = Item.query()
    print "The query length is "+str(len(itemsOfInterest.fetch(None)))
    if form.validate_on_submit():
        newItem = Item(id=str(uuid.uuid1()),item=form.item.data)
        print("myUUID is "+newItem.id)
        newItem.put()
        flash('New item added!')
        return redirect(url_for('index'))
    return render_template('index.html',
                           title='USI Help System',
                           itemsOfInterest=itemsOfInterest,
                           form=form
                           )
