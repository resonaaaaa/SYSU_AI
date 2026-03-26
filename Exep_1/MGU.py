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

    def equal(self, other):
        return equal(self, other)

    #判断是否与另一个谓词相反
    def is_opposite(self, other):
        return self.name == other.name and self.neg != other.neg

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
    
    #变量更名，替换谓词中的变量
    def rename(self, replace:dict):
        for i, x in enumerate(self.para):
            if x in replace:
                self.para[i] = replace[x]
        self.in_str = ("~" if self.neg else "") + self.name + "(" + ",".join(self.para) + ")"


def equal(p1:Predicate, p2:Predicate):
    if p1.name != p2.name:
        return False
    if len(p1.para) != len(p2.para):
        return False
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
            return self.name == other.name and self.neg != other.neg

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
            self.in_str = ("~" if self.neg else "") + self.name + "(" + ",".join(self.para) + ")"


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
    
        def apply_subst(self, subst:dict):
            for lit in self.literals:
                for i in range(len(lit.para)):
                    lit.rename(subst.keys(), subst.values())
            

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

    #替换谓词中的变量
def replace_pred(pred:Predicate, replace:dict):
        for i in range(len(pred.para)):
            pred.rename(replace.keys(), replace.values())

    #归结子句
def resolve(clause1:Clause, clause2:Clause):
        results = []
        for i, lit1 in enumerate(clause1.literals):
            for j, lit2 in enumerate(clause2.literals):
                if lit1.is_opposite(lit2):
                    subst = MGU(lit1, lit2) #建立变换的字典
                    #无法统一的情况
                    if subst is None:  
                        continue
                    new_literals = [] 
                    #新子句包含除了被消去的文字以外的其他文字
                    for k, other_lit in enumerate(clause1.literals):
                        if k != i:
                            p = Predicate(other_lit.get_pred_str())
                            new_literals.append(p)
                    for k, other_lit in enumerate(clause2.literals):
                        if k != j:
                            p = Predicate(other_lit.get_pred_str())
                            new_literals.append(p)
                    new_clause = Clause([])
                    new_clause.literals = new_literals
                    new_clause.apply_subst(subst)  #在新子句中给有关文字进行变换
                
                    unique = []
                    strs = set()
                    for lit in new_clause.literals:
                        s = lit.get_pred_str()
                        #如果已有该文字
                        if s in strs:
                            continue
                        #如果新子句中有矛盾的文字，则子句为无效
                        if any(lit.is_opposite(other) for other in new_clause.literals):
                            unique = None
                            break
                        strs.add(s)
                        unique.append(lit) 
                    if unique is None:
                        continue
                    new_clause.literals = unique
                    results.append((new_clause, i, j, subst))
        return results

    #将子句转换为谓词字符串元组
def clause_convert(clause:Clause):
        return tuple(lit.get_pred_str() for lit in clause.literals)

def is_empty_clause(clause:Clause):
        return len(clause.literals) == 0


def resolution_step(clause_list:list):
        steps = []
        clause_list_copy = clause_list[:] #切片复制，避免修改原始子句列表

        visited = set() #记录已访问的子句
        for idx, c in enumerate(clause_list_copy, start=1):
            steps.append((idx, clause_convert(c)))
            visited.add(clause_convert(c))

        #构造一个映射，用子句的id绑定索引
        clause_map = dict()
        for idx in range(len(clause_list_copy)):
            clause_map[id(clause_list_copy[idx])] = idx + 1
    
        next_idx = len(clause_list_copy) + 1

        to_process = clause_list_copy[:] #待处理子句列表
        processed = []   #已处理子句，避免重复处理
        #循环处理子句直到没有子句需要处理
        while to_process:
            c1 = to_process.pop(0)
            processed.append(c1)
            for c2 in clause_list_copy + processed:
                if c1 is c2: #不允许与自己进行归结
                    continue
                res = resolve(c1, c2)
                for new_clause, i, j, subst in res:
                    new_c = clause_convert(new_clause) 
                    if new_c in visited:
                        continue
                    visited.add(new_c)
                    clause_list_copy.append(new_clause)
                    to_process.append(new_clause)
                
                    # 查找 c1和c2 的索引，如果不存在就加到映射里
                    idx1 = clause_map.get(id(c1))
                    if idx1 is None:
                        idx1 = next_idx
                        steps.append((next_idx, clause_convert(c1)))
                        clause_map[id(c1)] = next_idx
                        next_idx += 1
                    idx2 = clause_map.get(id(c2))
                    if idx2 is None:
                        idx2 = next_idx
                        steps.append((next_idx, clause_convert(c2)))
                        clause_map[id(c2)] = next_idx
                        next_idx += 1

                    # 将新子句加入映射
                    steps.append((next_idx, new_c))
                    clause_map[id(new_clause)] = next_idx
                
                    #变量替换表
                    sub_str = ", ".join(f"{k} = {v}" for k, v in subst.items()) if subst else ""

                    #标明子句与文字信息
                    def lit_letter(_clause, lit_idx):
                        clause_idx = clause_map.get(id(_clause))
                
                        if len(_clause.literals) == 1:
                            return clause_idx
                        return f"{clause_idx}{'abcdefghijklmnopqrstuvwxyz'[lit_idx]}"

                    label1 = lit_letter(c1, i)
                    label2 = lit_letter(c2, j)

                    meta = f"R[{label1},{label2}]{{{sub_str}}}"
                    steps.append((meta, next_idx))
                    if is_empty_clause(new_clause):
                        return steps
                    next_idx += 1
        return steps

def test():
        p1 = Predicate("P(x,y)")
        p2 = Predicate("P(a,b)")
        p1.print_para()

def __main__():
        clause_list = []
        in_str = input("请输入子句集：")
        in_str = in_str.strip().strip("{}")
        s = in_str
        clause_strs = []
        i = 0
        #处理输入字符串，获取子句
        while i < len(s):
            if s[i] == '(':
                start = i + 1
                depth = 1
                while depth > 0 and i < len(s) - 1:
                    i += 1
                    if s[i] == '(':
                        depth += 1
                    elif s[i] == ')':
                        depth -= 1
                clause_strs.append(s[start:i].strip())
            i += 1


        #处理子句字符串，获取文字
        def split_literals(clause_str):
            literals = []
            current = ""
            depth = 0
            #正确处理括号，防止多参数的谓词被错误分割
            for char in clause_str:
                if char == ',' and depth == 0:
                    literals.append(current.strip())
                    current = ""
                else:
                    current += char
                    if char == '(':
                        depth += 1
                    elif char == ')':
                        depth -= 1
            if current.strip():
                literals.append(current.strip())
            return literals

        for clause_str in clause_strs:
            literals = split_literals(clause_str)
            clause_list.append(Clause(literals))
    
    
        for clause in clause_list:
            print(clause.print_clause())

        steps = resolution_step(clause_list)

        def get_clause(steps_list, idx):
            for k, v in steps_list:
                if isinstance(k, int) and k == idx:
                    return v
            return None

        def format_clause_tuple(tup):
            if not tup:
                return "()"
            return "(" + ",".join(tup) + ",)"

        i = 0
        while i < len(steps):
            key, val = steps[i]
            if isinstance(key, int) and i + 1 < len(steps) and isinstance(steps[i+1][0], str) and steps[i+1][1] == key:
                meta = steps[i+1][0]
                clause = val
                print(f"{key} {meta}={format_clause_tuple(clause)}")
                i += 2
                continue

            if isinstance(key, int):
                print(f"{key} {format_clause_tuple(val)}")
            else:
                if isinstance(val, int):
                    clause = get_clause(steps, val)
                    if clause is not None:
                        print(f"{val} {key}={format_clause_tuple(clause)}")
                    else:
                        print(f"{key}=()")
                else:
                    print(f"{key}={format_clause_tuple(val)}")
            i += 1

if __name__ == "__main__":    
        __main__()

