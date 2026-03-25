import re

#谓词类
class Predicate():
    def __init__(self,in_str):
        self.para = []
        self.neg = False
        self.in_str = in_str.strip()
        if in_str.startswith("~"):
            self.neg = True
            in_str = in_str[1:]

        self.name = in_str.split("(")[0] 
        self.para = in_str[len(self.name)+1:-1].split(",")

    def is_neg(self):
        return self.neg

    #判断是否与另一个谓词相反
    def is_opposite(self, other):
        return self.name == other.name and self.para == other.para and self.neg != other.neg

    def can_unify(self, other):
        if self.name != other.name:
            return False
        if len(self.para) != len(other.para):
            return False
        for p1, p2 in zip(self.para, other.para):
            if p1 != p2 and not (is_var(p1) or is_var(p2)):
                return False
        return True
    
    #返回整个谓词字符串
    def get_pred_str(self):
        return self.in_str
    
    def print_para(self):
        for p in self.para:
            print(p)
    
    #变量替换
    def rename(self,old_name,new_name):
        for x in self.para:
            if x in old_name:
                self.para[self.para.index(x)] = new_name[old_name.index(x)]
    

def equal(p1:Predicate, p2:Predicate):
    if p1.name != p2.name:
        return False
    if len(p1.para) != len(p2.para):
        return False
    for i in range(len(p1.para)):
        if p1.para[i] != p2.para[i]:
            return False
    return True

#子句类
class Clause():
    def __init__(self, literals_list):
        self.literals = []
        for lit in literals_list:
            self.literals.append(Predicate(lit))

    def print_clause(self):
        clause_str = ""
        for lit in self.literals:
            clause_str += lit.get_pred_str() + ","
        return clause_str[:-1]
    
    def equal(self, other):
        if len(self.literals) != len(other.literals):
            return False
        for lit in self.literals:
            if not any(lit.equal(other_lit) for other_lit in other.literals):
                return False
        return True

#判断是否为变量,规定变量为单个小写字母，从u到z
def is_var(x):
    return re.match(r"^[u-z]$", x) is not None

#判断是否为函数项,如(f(x,g(y)))
def is_func(x):
    return re.match(r"^\w+\(.*\)$", x) is not None

#判断是否为常量,规定常量为小写单词或u-z以外的小写字母
def is_const(x):
    return re.match(r"\w+", x) is not None and not is_var(x)

def MGU(p1:Predicate, p2:Predicate):
    if not p1.can_unify(p2):
        print("无法统一")
        return None
    
    replace = dict()
    for x, y in zip(p1.para, p2.para):
        if x != y:
            if is_var(x):
                replace[x] = y
            elif is_var(y):
                replace[y] = x
            else:
                print("无法统一")
                return None
    return replace

def replace_pred(pred:Predicate, replace:dict):
    for i in range(len(pred.para)):
        if pred.para[i] in replace:
            pred.para[i] = replace[pred.para[i]]

def resolve(clause1:Clause, clause2:Clause):
    results = []
    for i, lit1 in enumerate(clause1.literals):
        for j, lit2 in enumerate(clause2.literals):
            if lit1.is_opposite(lit2):
                replace = MGU(lit1, lit2)
                if replace is not None:
                    new_clause = Clause([])
                    for k, other_lit in enumerate(clause1.literals):
                        if k != i:
                            new_clause.literals.append(other_lit)
                    for k, other_lit in enumerate(clause2.literals):
                        if k != j:
                            new_clause.literals.append(other_lit)
                    for lit in new_clause.literals:
                        replace_pred(lit, replace)
                    results.append(tuple(lit.get_pred_str() for lit in new_clause.literals))
    return results, i+1, j+1


def test():
    p1 = Predicate("P(x,y)")
    p2 = Predicate("P(a,b)")
    p1.print_para()

def __main__():
    clause_list = []
    in_str = input("请输入子句集：")
    in_str = in_str.strip("{}")
    clause_strs = in_str.split("),(")
    for clause_str in clause_strs:
        literals = re.split(r"\s*,\s*", clause_str)
        for lit in literals:
            if lit == '(':
                literals.remove(lit)
            if lit.startswith('('):
                _lit = lit[1:]
                literals[literals.index(lit)] = _lit
            if lit == ')':
                literals.remove(lit)
            if lit == '':
                literals.remove(lit)
        clause_list.append(Clause(literals))   
    
    
    
    #test()

if __name__ == "__main__":    
    __main__()

