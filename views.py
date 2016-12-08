import thread
from google.appengine.api import datastore_errors
from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

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

def storeCat(myCat,type='category',url=""):
    myCat2=Category(name=myCat,type=type,url=url)
    myCat2.put()
    return myCat2

def storeProb(myProb, myAns, url=""):
    if myProb==None: myProb=""
    if myAns==None: myAns=""
    myProb2=Problem(problem=myProb,solution=myAns,url=url)
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
            if (node.nodeType() == "Category" and node.payload.name == request.form['selectedCat']) \
                    or node.nodeType() == "Problem":
                myObj = node
                break
        if myObj!=None:
            del roots[:]
            for thing in myObj.returnRootChildren():
                roots.append(thing)
    return render_template("index.html",roots=roots)
    # return redirect("static/wwindex.html")
    # return render_template("newindex.html")
    # return redirect("/template/newindex.html")


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
    print "The length of catList is "+str(len(catList))
    for category in catList:
        print category
        if str(request.args.get("id"))==str(category.id):
            myNode=category
            print "Found category "+category.name
            break
    if(myNode==None):
        for problem in probList:
            print problem
            if str(request.args.get("id")) == str(problem.id):
                myNode = problem
                print "Found problem " + problem.problem + " / " + problem.solution
                break
    baseNode=None
    print "Looking up "+str(request.args.get("id"))
    for tree in roots:
        print tree
        baseNode=tree.lookup(str(request.args.get("id")))
        if baseNode!=None: break
    if baseNode!=None:
        for node in baseNode.returnRootChildren():
            returnDict = {}
            returnDict['id']=node.payload.id
            if hasattr(node.payload,'name'):
                returnDict['name']=node.payload.name
                returnDict['type']=node.payload.type
                returnDict['url'] = node.payload.url
            elif hasattr(node.payload,'problem') and node.payload.problem!=None and node.payload.problem!="":
                returnDict['name'] = node.payload.problem
                returnDict['type'] = "problem"
                returnDict['solution'] = node.payload.solution
                returnDict['url'] = node.payload.url
            elif hasattr(node.payload,'solution') and node.payload.solution!=None and node.payload.solution!="":
                returnDict['name'] = node.payload.solution
                returnDict['type']="solution"
            returnList.append(returnDict)
    else:
        print "Could not find the root node."
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

@app.route('/_createRoot')
def create_root():
    myRoot = Node(storeCat(request.args.get("name")))
    roots.append(myRoot)
    print "There were "+str(len(Tree.query().fetch(None)))+" entries."
    Tree(tree=str(myRoot.convertTree())).put()
    print "Now there are "+str(len(Tree.query().fetch(None)))+" entries."
    return get_tree()

@app.route('/_createSubcat')
def create_subcat():
    newObj = {}
    if request.args.get("type")=='Subcategory':
        print "I will make a node!"
        baseNode = None
        print "Looking up " + str(request.args.get("parentId"))
        for tree in roots:
            baseNode = tree.lookup(str(request.args.get("parentId")))
            if baseNode != None:
                #print "There were " + str(len(Tree.query().fetch(None))) + " tree entries."
                print "There were " + str(len(Category.query().fetch(None))) + " category entries."
                newCat=storeCat(request.args.get("name"))
                baseNode.addSubNode(newCat)
                newObj={'id':newCat.id,'name':newCat.name,'type':newCat.type,'url':newCat.url}

                # trees = Tree.query()  # get item list
                # for tree in trees:  # find correct item
                #     roots.append(Node(ast.literal_eval(tree.tree)))

                trees = Tree.query()  # get item list
                for mytree in trees:  # find correct item
                    treeDict=ast.literal_eval(mytree.tree)
                    #print treeDict['node']
                    if str(treeDict['node'])==str(tree.payload.id):
                        print "Found match!"
                        # Tree(tree=str(myRoot.convertTree())).put()
                        mytree.tree=str(tree.convertTree())
                        mytree.put()
                        break
                print "Now there are " + str(len(Tree.query().fetch(None))) + " tree entries."
                print "Now there are " + str(len(Category.query().fetch(None))) + " category entries."
                break
        else:
            print "Parent node could not be found!"
    return jsonify(newObj)

    # myRoot = Node(storeCat(request.args.get("name")))
    # roots.append(myRoot)
    # print "There were "+str(len(Tree.query().fetch(None)))+" entries."
    # Tree(tree=str(myRoot.convertTree())).put()
    # print "Now there are "+str(len(Tree.query().fetch(None)))+" entries."
    # return get_tree()

def setupTree():
    if len(roots) == 0:
        metaData = Tree.query()
        if len(metaData.fetch(None)) == 0:
            root1 = Node(storeCat("Lawn Equipment"))
            roots.append(root1)
            lawnmower = root1.addSubNode(storeCat("Lawn Mower"))
            weedeater = root1.addSubNode(storeCat("Weed Eater"))
            edger=root1.addSubNode(storeCat("Edger"))

            wontStart = lawnmower.addSubNode(storeProb("Lawn mower won't start",None))
            ws1=wontStart.addSubNode(storeProb("Is there gas in the tank?","Put gas in the mower!"))
            ws2=ws1.addSubNode(storeProb("Will the mower jump start?","Replace the battery!"))
            ws3=ws2.addSubNode(storeProb(
                "Do the spark plugs appear clean?",
                "Clear or replace the plugs!",
                url="https://goo.gl/FJneX0"))
            wontCut = lawnmower.addSubNode(storeProb("Mower isn't cutting the grass well",None))
            wc1=wontCut.addSubNode(storeProb(
                "Is the grass a reasonable height?",
                "Raise the cutting height on your lawn mower"
            ))
            wc2=wc1.addSubNode(storeProb(
                "Does the blade appear to be sharp?",
                "Replace or sharpen the blade",
                "https://goo.gl/ANuuah"
            ))

            toro = lawnmower.addSubNode(storeCat("Toro",type='part'))
            honda = lawnmower.addSubNode(storeCat("Honda",type='part'))
            craftsman = lawnmower.addSubNode(storeCat("Craftsman",type='part'))
            honda.addSubNode(storeCat("Spark Plug", type='part',url="https://goo.gl/4988HT"))
            honda.addSubNode(storeCat("Blade", type='part', url="https://goo.gl/6IzHDH"))
            honda.addSubNode(storeCat("Battery", type='part', url="https://goo.gl/j32Qs0"))
            toro.addSubNode(storeCat("Spark Plug", type='part',url="https://goo.gl/iSq3IM"))
            toro.addSubNode(storeCat("Blade", type='part', url="https://goo.gl/awrF4W"))
            toro.addSubNode(storeCat("Battery", type='part', url="https://goo.gl/hxFbMM"))
            craftsman.addSubNode(storeCat("Spark Plug", type='part',url="https://goo.gl/uMbjzb"))
            craftsman.addSubNode(storeCat("Blade", type='part', url="https://goo.gl/6mcSAe"))
            craftsman.addSubNode(storeCat("Battery", type='part', url="https://goo.gl/Txykkp"))

            root2 = Node(storeCat("Smartphone"))
            roots.append(root2);
            android=root2.addSubNode(storeCat("Google Android"))
            apple=root2.addSubNode(storeCat("Apple iOS"))

            slow=android.addSubNode(storeProb("My phone is slow",None))
            sl1=slow.addSubNode(storeProb(
                "Has the phone been restarted recently?","Reboot the phone"))
            sl2=sl1.addSubNode(storeProb(
                "Are there only a few apps open?","Close the apps you aren't actively using"))
            sl3=sl2.addSubNode(storeProb(
                "Is atleast 90% of the phone storage free?","Removed unused apps or upgrade the storage"))
            app=android.addSubNode(storeProb("I want to develop an app","Follow a tutorial",None))
            app.addSubNode(storeProb(
                "Have you tried following a tutorial?",
                "Use an online tutorial",
                url="https://developer.android.com/training/basics/firstapp/index.html"))

            slow=apple.addSubNode(storeProb("My phone is slow",None))
            sl1=slow.addSubNode(storeProb(
                "Has the phone been restarted recently?","Reboot the phone"))
            sl2=sl1.addSubNode(storeProb(
                "Are there only a few apps open?","Close the apps you aren't actively using"))
            sl3=sl2.addSubNode(storeProb(
                "Is atleast 90% of the phone storage free?","Removed unused apps or upgrade the storage"))
            app=apple.addSubNode(storeProb("I want to develop an app","Follow a tutorial",None))
            app.addSubNode(storeProb(
                "Have you tried following a tutorial?",
                "Use an online tutorial",
                url="https://developer.apple.com/library/content/referencelibrary/GettingStarted/DevelopiOSAppsSwift/"))


            moto=android.addSubNode(storeCat("Motorola",type='part'))
            samsung=android.addSubNode(storeCat("Samsung", type='part'))
            huawei=android.addSubNode(storeCat("Huawei", type='part'))
            moto.addSubNode(storeCat("Case",type='part',url="https://goo.gl/aSNG2U"))
            samsung.addSubNode(storeCat("Case",type='part',url="https://goo.gl/T10QPU"))
            huawei.addSubNode(storeCat("Case",type='part',url="https://goo.gl/frSgRq"))
            apple.addSubNode(storeCat("Case",type='part',url="https://goo.gl/6vclg7"))

            root1.printTree()
            root2.printTree()

            testTree=str(root1.convertTree())
            print testTree

            # treeDict = root1.convertTree()
            Tree(tree=testTree).put()
            Tree(tree=str(root2.convertTree())).put()
            # r1Prime = Node(treeDict)
            # print r1Prime

            print root1
            print root2

        else:
            for probsol in Problem.query(): probList.append(probsol)
            for cat in Category.query(): catList.append(cat)
            trees = Tree.query()  # get item list
            for tree in trees:  # find correct item
                roots.append(Node(ast.literal_eval(tree.tree)))
            for root in roots:
                root.printTree();
            print "Length of probList is " + str(len(probList))
            print "Length of catList is " + str(len(catList))