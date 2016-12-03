from google.appengine.ext import ndb
import uuid
import types
import config
from threading import Lock
import views

class Item(ndb.Model):

    id=ndb.StringProperty()
    models=ndb.StringProperty(repeated=True)
    item=ndb.StringProperty()

    def __init__(self,*args,**kwargs):
        super(Item, self).__init__(*args, **kwargs)
        if kwargs.has_key('id'): self.id=kwargs['id']
        if kwargs.has_key('item'): self.item=kwargs['item']

    def addModel(self,model):
        self.models.append(model)

class OldUser(ndb.Model):

    def __init__(self,id,nickname,email):
        self.id=id
        self.nickname=nickname
        self.email=email

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    @property
    def is_authenticated(self):
        return True

class Contact(ndb.Model):

    #Stores comment along with name and email for reply purposes
    #Currently stored contacts can only be deleted through admin server
    name=ndb.StringProperty()
    email=ndb.StringProperty()
    comments=ndb.TextProperty()

    def __init__(self,*args,**kwargs):
        super(Contact, self).__init__(*args, **kwargs)
        if kwargs.has_key('name'): self.id=kwargs['name']
        if kwargs.has_key('email'): self.item=kwargs['email']
        if kwargs.has_key('comments'): self.item = kwargs['comments']

class Category(ndb.Model):
    #id=""
    name=ndb.StringProperty()
    id=ndb.StringProperty()

    def __init__(self,*args,**kwargs):
        super(Category, self).__init__(*args, **kwargs)
        # lock = Lock()
        # with lock:
        #     views.counter += 1
        #     print (views.counter)
        if kwargs.has_key('name'): self.id=kwargs['name']
        if kwargs.has_key('id'): self.id=kwargs['id']
        else:  self.id=str(uuid.uuid1())

class Problem(ndb.Model):
    problem=ndb.StringProperty()
    solution=ndb.StringProperty()
    id=ndb.StringProperty()

    def __init__(self,*args,**kwargs):
        super(Problem, self).__init__(*args, **kwargs)
        if kwargs.has_key('problem'): self.id=kwargs['problem']
        if kwargs.has_key('solution'): self.id=kwargs['solution']
        if kwargs.has_key('id'): self.id=kwargs['id']
        else: self.id=str(uuid.uuid1())

class Node(ndb.Model):
    payload=ndb.PickleProperty()
    id=ndb.StringProperty()
    lft=ndb.PickleProperty()
    rgt=ndb.PickleProperty()

    def getObj(self, guid):
        for myCat in views.catList:
            if myCat.id==guid:
                return myCat
        for myProb in views.probList:
            if myProb.id==guid:
                return myProb
        return None

    def lookup(self,idStr):
        if (str(self.id) == str(idStr)): return self
        else:
            if self.lft != None: self.lft.lookup(idStr)
            if self.rgt != None: self.rgt.lookup(idStr)
            return None

    def parseNode(self, inDict):
        if (not inDict.has_key('lft') and not inDict.has_key('rgt')):
            return Node(self.getObj(inDict['node']))
        elif (inDict.has_key('lft') and not inDict.has_key('rgt')):
            return Node(self.getObj(inDict['node']), lft=self.parseNode(inDict['lft']))
        elif (inDict.has_key('rgt') and not inDict.has_key('lft')):
            return Node(self.getObj(inDict['node']), rgt=self.parseNode(inDict['rgt']))
        else:
            return Node(self.getObj(inDict['node']), lft=self.parseNode(inDict['lft']), rgt=self.parseNode(inDict['rgt']))

    def __init__(self, payload, lft=None, rgt=None, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        if isinstance(payload, types.DictionaryType):
            # treeDict=ast.literal_eval(payload)
            myLft = self.parseNode(payload['lft'])
            self.id = str(payload['node'])
            self.payload = self.getObj(payload['node'])
            # payload.put()
            self.lft = myLft
            self.rgt = None
        else:
            self.id = str(uuid.uuid1())
            self.payload = payload
            #payload.put()
            self.lft = lft
            self.rgt = rgt


    # def addNodes(self,newCat):

    def addSibling(self,sibNode,newNode):
        if sibNode.rgt==None: sibNode.rgt=newNode
        else: self.addSibling(sibNode.rgt,newNode)

    def addChild(self,child):
        if self.lft==None: self.lft=child;
        else: self.addSibling(self.lft,child)

    def addSubNode(self,payload):
        retNode=Node(payload,None,None)
        self.addChild(retNode)
        return retNode

    def nodeType(self):
        if isinstance(self.payload, Category): return "Category"
        else: return "Problem"

    def returnRootChildren(self):
        myKids=[]
        myNode=self.lft;
        while myNode!=None:
            myKids.append(myNode)
            myNode=myNode.rgt
        return myKids

    def spaceMe(self,scount):
        spaceStr = ""
        while scount > 0:
            spaceStr += " ";
            scount -= 1
        return spaceStr

    def payloadVal(self,payload):
        if payload.problem != None:
            return payload.problem
        else:
            return payload.solution

    def printTree(self,myNode=None, scount=0):
        if myNode == None:
            myNode=self
        if isinstance(myNode.payload, Category):
            if myNode.rgt == None and myNode.lft == None:
                print self.spaceMe(scount) + myNode.payload.name
                views.catList.append(myNode.payload)
            else:
                if myNode.lft != None:
                    print self.spaceMe(scount) + myNode.payload.name
                    views.catList.append(myNode.payload)
                    self.printTree(myNode.lft, scount + 4)
                if myNode.rgt != None:
                    if myNode.lft == None: print self.spaceMe(scount) + myNode.payload.name
                    views.catList.append(myNode.payload)
                    self.printTree(myNode.rgt, scount)

        else:
            if myNode.rgt == None and myNode.lft == None:
                print self.spaceMe(scount) + self.payloadVal(myNode.payload)
                views.probList.append(myNode.payload)
            else:
                if myNode.lft != None:
                    print self.spaceMe(scount) + self.payloadVal(myNode.payload)
                    views.probList.append(myNode.payload)
                    self.printTree(myNode.lft, scount + 4)
                if myNode.rgt != None:
                    if myNode.lft == None:
                        print self.spaceMe(scount) + self.payloadVal(myNode.payload)
                        views.probList.append(myNode.payload)
                    self.printTree(myNode.rgt, scount)

    def convertTree(self, myNode=None, scount=0):

        if myNode == None:
            myNode = self

        if myNode.rgt == None and myNode.lft == None:
            print self.spaceMe(scount) + myNode.payload.id
            return { 'node': myNode.payload.id }
        else:
            if myNode.lft != None:
                if myNode.rgt == None:
                    print self.spaceMe(
                        scount) + "left guid: " + myNode.lft.payload.id + " node guid: " + myNode.payload.id
                    return {'node':myNode.payload.id, 'lft':self.convertTree(myNode.lft, scount + 4)}
                else:
                    print self.spaceMe(
                        scount) + "left guid: " + myNode.lft.payload.id + " node guid: " + myNode.payload.id + " right guid: " + myNode.rgt.payload.id
                    return { 'node': myNode.payload.id, 'lft': self.convertTree(myNode.lft, scount + 4), 'rgt': self.convertTree(myNode.rgt, scount)}
                self.convertTree(myNode.lft, scount + 4)
            #if myNode.rgt != None:
                #if myNode.lft == None:
                    #print self.spaceMe(scount) + "right guid: " + myNode.rgt.payload.id + " node guid: " + myNode.payload.id
                #self.convertTree(myNode.rgt, scount)

    # def addProblem(self,name):
    #    retProb=Problem(name,self.rgt,self.rgt+1)

class Tree(ndb.Model):
    tree = ndb.StringProperty()

    def __init__(self,*args,**kwargs):
        super(Tree, self).__init__(*args, **kwargs)
        if kwargs.has_key('tree'): self.id=kwargs['tree']


class UserClass(ndb.Model):
    # class UserClass():
    # username, email, password for each account
    # rights is the type of account:
    # 0: Anonymous - can only view
    # 1: Normal - can make edits as well as view content
    # 2: Superuser - can make edits, view content, and restrict normal users
    # 3: Admin - complete control over system
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    rights = ndb.StringProperty()

    def __init__(self,*args, **kwargs):
        super(UserClass, self).__init__(*args, **kwargs)
        if kwargs.has_key('username'): self.name = kwargs['username']
        if kwargs.has_key('email'): self.name = kwargs['email']
        if kwargs.has_key('password'): self.name = kwargs['password']
        if kwargs.has_key('rights'): self.name = kwargs['rights']

