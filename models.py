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
    type=ndb.StringProperty()
    url=ndb.StringProperty()

    def __init__(self,*args,**kwargs):
        super(Category, self).__init__(*args, **kwargs)
        # lock = Lock()
        # with lock:
        #     views.counter += 1
        #     print (views.counter)
        if kwargs.has_key('name'): self.id=kwargs['name']
        if kwargs.has_key('type'): self.id=kwargs['type']
        if kwargs.has_key('url'): self.id=kwargs['url']
        else: self.type='category'
        if kwargs.has_key('id'): self.id=kwargs['id']
        else: self.id=str(uuid.uuid1())

class Problem(ndb.Model):
    problem=ndb.StringProperty()
    solution=ndb.StringProperty()
    id=ndb.StringProperty()
    url=ndb.StringProperty()

    def __init__(self,*args,**kwargs):
        super(Problem, self).__init__(*args, **kwargs)
        if kwargs.has_key('problem'): self.id=kwargs['problem']
        if kwargs.has_key('solution'): self.id=kwargs['solution']
        if kwargs.has_key('url'): self.id = kwargs['url']
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
        print "Examining "+str(self.id)
        if (str(self.id) == str(idStr)): return self
        else:
            myVal = None
            if self.lft!=None:
                myVal = self.lft.lookup(idStr)
            if myVal==None and self.rgt!=None:
                myVal=self.rgt.lookup(idStr)
            return myVal

    def parseNode(self, inDict):
        if (not inDict.has_key('lft') and not inDict.has_key('rgt')):
            return Node(self.getObj(inDict['node']),id=inDict['node'])
        elif (inDict.has_key('lft') and not inDict.has_key('rgt')):
            return Node(self.getObj(inDict['node']), lft=self.parseNode(inDict['lft']),id=inDict['node'])
        elif (inDict.has_key('rgt') and not inDict.has_key('lft')):
            return Node(self.getObj(inDict['node']), rgt=self.parseNode(inDict['rgt']),id=inDict['node'])
        else:
            return Node(self.getObj(inDict['node']), lft=self.parseNode(inDict['lft']), rgt=self.parseNode(inDict['rgt']),id=inDict['node'])

    def __init__(self, payload, lft=None, rgt=None, id=None, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        if isinstance(payload, types.DictionaryType):
            # treeDict=ast.literal_eval(payload)
            if 'lft' in payload:
                myLft = self.parseNode(payload['lft'])
                self.lft = myLft
            else:
                # print payload['lft']
                self.lft = None
            self.id = str(payload['node'])
            self.payload = self.getObj(payload['node'])
            # payload.put()
            self.rgt = None
        else:
            # Very interesting bug (2016-12-05 WW)
            # if(id==None): self.id = str(uuid.uuid1())
            if (id == None): self.id = str(payload.id)
            else: self.id=id
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

    def returnDistantProgeny(self):
        if self.lft==None:  return self
        else: return self.lft.returnDistantProgeny()

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
                print self.spaceMe(scount) + myNode.payload.name + " (" + myNode.payload.id + ")"
                views.catList.append(myNode.payload)
            else:
                if myNode.lft != None:
                    print self.spaceMe(scount) + myNode.payload.name + " (" + myNode.payload.id + ")"
                    views.catList.append(myNode.payload)
                    self.printTree(myNode.lft, scount + 4)
                if myNode.rgt != None:
                    if myNode.lft == None:
                        print self.spaceMe(scount) + myNode.payload.name + " (" + myNode.payload.id + ")"
                        # This was another bug (12/5/2016 WW); too many entries in catList ... needed indenting
                        views.catList.append(myNode.payload)
                    self.printTree(myNode.rgt, scount)

        else:
            if myNode.rgt == None and myNode.lft == None:
                print self.spaceMe(scount) + self.payloadVal(myNode.payload) + " (" + myNode.payload.id + ")"
                views.probList.append(myNode.payload)
            else:
                if myNode.lft != None:
                    print self.spaceMe(scount) + self.payloadVal(myNode.payload) + " (" + myNode.payload.id + ")"
                    views.probList.append(myNode.payload)
                    self.printTree(myNode.lft, scount + 4)
                if myNode.rgt != None:
                    if myNode.lft == None:
                        print self.spaceMe(scount) + self.payloadVal(myNode.payload) + " (" + myNode.payload.id + ")"
                        views.probList.append(myNode.payload)
                    self.printTree(myNode.rgt, scount)

    def convertTree(self, myNode=None):
        if myNode == None: myNode = self
        if myNode.rgt == None and myNode.lft == None: return { 'node': myNode.payload.id }
        elif myNode.rgt!=None and myNode.lft==None:
            return {'node': myNode.payload.id, 'rgt': self.convertTree(myNode=myNode.rgt)}
        elif myNode.lft!=None and myNode.rgt==None:
            return {'node': myNode.payload.id, 'lft': self.convertTree(myNode=myNode.lft)}
        else:
            return {'node': myNode.payload.id,
                    'lft': self.convertTree(myNode=myNode.lft),
                    'rgt': self.convertTree(myNode=myNode.rgt)}

    def convertTreeOld(self, myNode=None, scount=0):

        if myNode == None:
            myNode = self

        if myNode.rgt == None and myNode.lft == None:
            print self.spaceMe(scount) + myNode.payload.id
            return {'node': myNode.payload.id}
        else:
            if myNode.lft != None:
                if myNode.rgt == None:
                    print self.spaceMe(
                        scount) + "left guid: " + myNode.lft.payload.id + " node guid: " + myNode.payload.id
                    return {'node': myNode.payload.id, 'lft': self.convertTree(myNode.lft, scount + 4)}
                else:
                    print self.spaceMe(
                        scount) + "left guid: " + myNode.lft.payload.id + " node guid: " + myNode.payload.id + " right guid: " + myNode.rgt.payload.id
                    return {'node': myNode.payload.id, 'lft': self.convertTree(myNode.lft, scount + 4),
                            'rgt': self.convertTree(myNode.rgt, scount)}
                self.convertTree(myNode.lft, scount + 4)
                # if myNode.rgt != None:
                # if myNode.lft == None:
                # print self.spaceMe(scount) + "right guid: " + myNode.rgt.payload.id + " node guid: " + myNode.payload.id
                # self.convertTree(myNode.rgt, scount)

class Tree(ndb.Model):
    # Another interesting bug: BadValueError: Indexed value tree must be at most 1500 bytes [was StringProperty()]
    tree = ndb.TextProperty()

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

