import re

#谓词类
class Predicate:
    def __init__(self, in_str):
        s = in_str.strip()
        self.neg = False    #判断前缀
        if s.startswith("~"):
            self.neg = True
            s = s[1:]
        #分割谓词名称与参数
        if "(" in s and s.endswith(")"):
            self.name = s.split("(")[0]
            params = s[len(self.name) + 1:-1]
            self.params = [p.strip() for p in params.split(",")] if params else []
        else:
            self.name = s
            self.params = []

    def is_neg(self):
        return self.neg

    #返回完整的谓词字符串
    def get_pred_str(self):
        return ("~" if self.neg else "") + self.name + ("(" + ",".join(self.params) + ")" if self.params else "")

    def is_opposite(self, other):
        return self.name == other.name and self.neg != other.neg

    #变量改名
    def rename(self, subst: dict):
        for i, p in enumerate(self.params):
            if p in subst:
                self.params[i] = subst[p]


class Clause:
    def __init__(self, literals_list):
        self.literals = []  #文字列表
        if literals_list:
            for lit in literals_list:
                self.literals.append(Predicate(lit))

    def print_clause(self):
        if not self.literals:  #空子句
            return "()"
        if len(self.literals) == 1: #单文字
            return self.literals[0].get_pred_str()
        return "(" + ",".join(lit.get_pred_str() for lit in self.literals) + ")"


# 规定变量是小写字母，且只能是u~z
def is_var(x: str) -> bool:
    return re.match(r"^[u-z]$", x) is not None


def MGU(p1: Predicate, p2: Predicate):
    #谓词不同名，或者参数数量不同，无法统一
    if p1.name != p2.name or len(p1.params) != len(p2.params):
        return None
    subst = {}   #变量替换的字典
    for a, b in zip(p1.params, p2.params):
        if a == b:
            continue
        if is_var(a) and not is_var(b):
            subst[a] = b
        elif is_var(b) and not is_var(a):
            subst[b] = a
        elif is_var(a) and is_var(b):
            subst[a] = b
        else:
            return None
    return subst

#给整个子句的谓词变量替换
def apply_subst(clause, subst: dict):
    for lit in clause.literals:
        lit.rename(subst)

#归结
def resolve(c1: Clause, c2: Clause):
    results = []
    for i, l1 in enumerate(c1.literals):
        for j, l2 in enumerate(c2.literals):
            if l1.is_opposite(l2):   #找到一对相反的文字
                subst = MGU(l1, l2)  #建立替换字典
                if subst is None:  #无法统一的情况
                    continue

                #生成新子句，不包括被消掉的文字
                new_literals = []
                for k, other in enumerate(c1.literals):  
                    if k != i:
                        new_literals.append(Predicate(other.get_pred_str()))
                for k, other in enumerate(c2.literals):
                    if k != j:
                        new_literals.append(Predicate(other.get_pred_str()))
                new_clause = Clause([])
                new_clause.literals = new_literals

                apply_subst(new_clause, subst)   #在整个新子句中应用替换
                # 去重并检查矛盾
                visited = set()
                unique = []
                paradox = False 
                for lit in new_clause.literals:
                    s = lit.get_pred_str()
                    if s in visited:
                        continue
                    if any(lit.is_opposite(other) for other in new_clause.literals):  #有矛盾的情况
                        paradox = True
                        break
                    visited.add(s)
                    unique.append(lit)
                if paradox:
                    continue
                new_clause.literals = unique
                results.append((new_clause, i, j, subst))
    return results

#从Clasue类转换为字符串
def clause_convert(clause: Clause):
    return tuple(lit.get_pred_str() for lit in clause.literals)


def is_empty_clause(clause: Clause):
    return len(clause.literals) == 0

#处理输入
def input_process(in_str: str):
    s = in_str.strip().strip("{}")
    clause_strs = []
    i = 0

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

    #将子句分割为文字
    def split_literals(clause_str):
        literals = []
        cur = ""
        depth = 0
        for ch in clause_str:
            if ch == ',' and depth == 0:
                if cur.strip(): 
                    literals.append(cur.strip())
                cur = ""
            else:
                cur += ch
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
        if cur.strip():
            literals.append(cur.strip())
        return literals

    clause_list = []
    for cs in clause_strs:
        lits = split_literals(cs)
        clause_list.append(Clause(lits))
    return clause_list


def format_clause(clause):
    var_map = {}  #变量映射字典
    next_var = 0 
    pred_list = []  #谓词的规范化表示列表
    for lit in clause.literals:
        params = []     #参数列表
        for p in lit.params:
            if is_var(p):
                if p not in var_map:
                    var_map[p] = f"?{next_var}"   #加入映射表
                    next_var += 1   
                params.append(var_map[p])
            else:
                params.append(p)
        pred_list.append((lit.name, lit.neg, tuple(params)))  #将名称、前缀和所有参数都加入谓词列表
    pred_list.sort()  #对谓词列表进行排序，保证规范化的一致
    return tuple(pred_list)

#判断子句中有无矛盾
def has_paradox(clause):
    visited = set()
    for lit in clause.literals:
        visited.add((lit.name, lit.neg, tuple(lit.params)))
    for name, neg, params in [(x[0], x[1], x[2]) for x in visited]:
        if (name, not neg ,params) in visited:
            return True
    return False

#判断新子句是否被已访问的子句包含，被包含的新子句没有有效的信息，跳过
def is_subsumed(new_clause, visited_clause_list):
    new_set = set((n, neg, params) for (n, neg, params) in new_clause)
    for visited in visited_clause_list:
        exist_set = set((n, neg, params) for (n, neg, params) in visited)
        if exist_set.issubset(new_set):  #如果存在一个已访问的子句是新子句的子集，说明新子句被包含了，跳过
            return True
    return False

#生成归结步骤
def resolution_step(clause_list):
    steps = []
    clause_list_copy = clause_list[:]
    visited = set()
    visited_clause_list = []
    #建立一个子句ID与索引的映射表
    clause_map = {id(clause_list_copy[k]): k + 1 for k in range(len(clause_list_copy))}
    next_idx = len(clause_list_copy) + 1

    #将初始子句加入步骤列表
    for idx, c in enumerate(clause_list_copy, start=1):
        steps.append((idx, clause_convert(c)))
        formatted = format_clause(c) 
        visited.add(formatted)
        visited_clause_list.append(formatted)

    single_queue = [c for c in clause_list_copy if len(c.literals) == 1]   #单文字子句,先处理，因为它们更好消去
    general_queue = [c for c in clause_list_copy if len(c.literals) != 1 and c not in single_queue]  #一般子句
    to_process = single_queue + general_queue
    processed = []
    processed_pairs = set()

    while to_process:
        c1 = to_process.pop(0)
        processed.append(c1)
        for c2 in clause_list_copy:
            if c1 is c2:
                continue
            pair_id = tuple(sorted((id(c1), id(c2))))  #标识处理过的子句对，避免重复处理
            if pair_id in processed_pairs:
                continue
            processed_pairs.add(pair_id)

            res = resolve(c1, c2)   #产生新子句，获取新子、消掉的文字索引和替换字典
            for new_clause, i, j, subst in res: 
                if has_paradox(new_clause): #矛盾子句跳过
                    continue

                formatted = format_clause(new_clause) 
                if is_subsumed(formatted, visited_clause_list ):  #被已访问的子句包含了，说明新子句没有有效信息，跳过
                    continue

                if formatted in visited:  #访问过的子句跳过
                    continue

                visited.add(formatted)
                visited_clause_list .append(formatted)
                clause_list_copy.append(new_clause)
                to_process.append(new_clause)

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

                steps.append((next_idx, clause_convert(new_clause)))
                clause_map[id(new_clause)] = next_idx

                sub_str = ", ".join(f"{k}={v}" for k, v in subst.items()) if subst else ""

                def lit_label(_clause, lit_idx):
                    cidx = clause_map.get(id(_clause))
                    if len(_clause.literals) == 1:
                        return str(cidx)
                    return f"{cidx}{'abcdefghijklmnopqrstuvwxyz'[lit_idx]}"

                label1 = lit_label(c1, i)
                label2 = lit_label(c2, j)
                resolve_msg = f"R[{label1},{label2}]{{{sub_str}}}"
                steps.append((resolve_msg, next_idx))
                if is_empty_clause(new_clause):
                    return steps
                next_idx += 1
    return steps


def main():
    in_str = input("请输入子句集：\n")
    clause_list = input_process(in_str)

    steps = resolution_step(clause_list)

    def get_clause(steps_list, idx):
        for k, v in steps_list:
            if isinstance(k, int) and k == idx:
                return v
        return None

    def convert2str(clause_tuple):
        if not clause_tuple:
            return "()"
        if len(clause_tuple) == 1:
            return "(" + clause_tuple[0] + ",)"
        return "(" + ",".join(clause_tuple) + ")"

    i = 0
    while i < len(steps):
        key, val = steps[i]
        #若下一个步骤的子句与当前步骤的key相同且是一个字符串，说明这是归结的步骤
        if isinstance(key, int) and i + 1 < len(steps) and isinstance(steps[i+1][0], str) and steps[i+1][1] == key:
            resolve_msg = steps[i+1][0] 
            clause = val
            print(f"{key} {resolve_msg}={convert2str(clause)}")
            i += 2
            continue
        #一般的子句输出
        if isinstance(key, int):
            print(f"{key} {convert2str(val)}")
        else: 
            if isinstance(val, int):  
                clause = get_clause(steps, val)
                if clause is not None:
                    print(f"{val} {key}={convert2str(clause)}")
                else:
                    print(f"{key}=()")
            else:
                print(f"{key}={convert2str(val)}")
        i += 1


if __name__ == "__main__":
    main()

