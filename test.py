

class ClassA():
    def __init__(self,x,y):
        print 'this is ClassA', x, y
        self.x = x
        self.y = y
    
    def methodA(self):
        print 'methodA: %s %s' % (self.x, self.y)


class ClassB(ClassA):
    def __init__(self, **kwargs):
        super(ClassB, self).__init__(x=kwargs.get('x'), y=kwargs.get('y'))
        #ClassA.__init__(self, x, y)
    
    

objA = ClassA(1,2)
objA.methodA()
print '-'*10
objB = ClassB(x=3,y=4)
objB.methodA()