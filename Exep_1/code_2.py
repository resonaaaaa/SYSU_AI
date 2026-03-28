class Predicate:
    def __init__(self, str_in):
        self.para = []
        s = str_in.strip()
        if len(s) == 0:
            return
        if s[0] == ',':
            s = s[1:]
        if '(' in s:
            name, rest = s.split('(', 1)
            name = name.strip()
            self.para.append(name)
            inner = rest.rsplit(')', 1)[0]
            if inner.strip() == '':
                return
            parts = [p.strip() for p in inner.split(',') if p.strip() != '']
            for p in parts:
                self.para.append(p)
        else:
            self.para.append(s)

    
    def copy(self, para_list):
        for element in para_list:
            self.para.append(element)

    def replace(self, old_name, copy_name):
        for i in range(len(self.para)):
            for j in range(len(old_name)):
                if self.para[i] == old_name[j]:
                    self.para[i] = copy_name[j]

    def is_opposite(self, other):
        return self.get_name() == other.get_name() and self.is_neg() != other.is_neg()

    def is_neg(self):
        return self.para[0][0] == '~'

    def get_name(self):
        if self.is_neg():
            return self.para[0][1:]
        else:
            return self.para[0]


def predicate_to_str(p: Predicate) -> str:
    if len(p.para) > 1:
        return p.para[0] + "(" + ",".join(p.para[1:]) + ")"
    return p.para[0]


def format_clause_for_output(clause_in):
    parts = [predicate_to_str(cl) for cl in clause_in]
    if len(parts) == 0:
        return "()"
    if len(parts) == 1:
        return "(" + parts[0] + ",)"
    return "(" + ",".join(parts) + ")"


def print_clause(clause_in):
    clause_str = ""
    if len(clause_in) > 1:
        clause_str += "("
    for i in range(len(clause_in)):
        clause_str += clause_in[i].para[0]
        if len(clause_in[i].para) > 1:
            clause_str += "("
            for j in range(1, len(clause_in[i].para)):
                clause_str += clause_in[i].para[j]
                if j < len(clause_in[i].para) - 1:
                    clause_str += ","
            clause_str += ")"
        if i < len(clause_in) - 1:
            clause_str += ","
    if len(clause_in) > 1:
        clause_str += ")"
    return clause_str


def print_msg(key, i, j, old_name, copy_name):
    
    left = str(i + 1)
    right = str(j + 1)
    if len(copy_name) == 0 and len(clause_set[i]) != 1:
        left = left + chr(key + 97)
    right = right + chr(key + 97)
    # 生成替换表
    if len(old_name) > 0:
        subs = ", ".join(f"{old_name[k]} = {copy_name[k]}" for k in range(len(old_name)))
    else:
        subs = ""
    msg = f"{len(clause_set)} R[{left},{right}]{{{subs}}}="
    return msg


def end_loop(new_clause, clause_set):
    if len(new_clause) == 0:
        return True
    # 如果新子句是单文字，检查是否与已有单文字子句构成矛盾
    if len(new_clause) == 1:
        for i in range(len(clause_set) - 1):
            if len(clause_set[i]) == 1 and new_clause[0].get_name() == clause_set[i][0].get_name() and new_clause[0].para[1:] == clause_set[i][0].para[1:] and new_clause[0].is_neg() != clause_set[i][0].is_neg():
                print(f"{len(clause_set) + 1} R[{i+1},{len(clause_set)}]={{}}=()")
                return True
    return False

def main():
    global clause_set
    clause_set = []
    # 读取输入子句集，格式示例：{(P(a,z),),(A(x),),(~P(y,mike),~A(tony))}
    in_str = input("请输入子句集（例如：{(P(a,z),),(A(x),),(~P(y,mike),~A(tony))}）：\n").strip()
  
   
        # 解析输入，参考 MGU.py 的解析逻辑
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

        # 将子句内部按顶层逗号分割成文字
    def split_literals(clause_str):
            literals = []
            current = ""
            depth = 0
            for char in clause_str:
                if char == ',' and depth == 0:
                    if current.strip():
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

    clauses = []
    for cs in clause_strs:
            lits = split_literals(cs)
            if len(lits) == 1:
                clauses.append(lits[0])
            else:
                clauses.append("(" + ",".join(lits) + ")")

    for clause_in in clauses:
        if clause_in[0] == '(':
            clause_in = clause_in[1:-1]
        clause_in = clause_in.replace(' ', '')
        clause_set.append([])
        tmp = ""
        for j in range(len(clause_in)):
            tmp += clause_in[j]
            if clause_in[j] == ')':
                clause_tmp = Predicate(tmp)
                clause_set[-1].append(clause_tmp)
                tmp = ""

    # 输出初始子句，按照 todo 要求的格式编号
    for i in range(len(clause_set)):
        print(f"{i+1} {format_clause_for_output(clause_set[i])}")

    status = True
    while status:
        for i in range(len(clause_set)):
            if not status:
                break
            if len(clause_set[i]) == 1:
                for j in range(len(clause_set)):
                    if not status:
                        break
                    if i == j:
                        continue
                    old_name = []
                    copy_name = []
                    key = -1
                    for k in range(len(clause_set[j])):
                        if clause_set[i][0].is_opposite(clause_set[j][k]):
                            key = k
                            for l in range(1, len(clause_set[j][k].para)):
                                if len(clause_set[j][k].para[l]) == 1:
                                    old_name.append(clause_set[j][k].para[l])
                                    copy_name.append(clause_set[i][0].para[l])
                                elif len(clause_set[i][0].para[l]) == 1:
                                    old_name.append(clause_set[i][0].para[l])
                                    copy_name.append(clause_set[j][k].para[l])
                                elif clause_set[j][k].para[l] != clause_set[i][0].para[l]:
                                    key = -1
                                    break
                            if key != -1:
                                break
                    if key == -1:
                        continue
                    new_clause = []
                    for k in range(len(clause_set[j])):
                        if k != key:
                            p = Predicate("")
                            p.copy(clause_set[j][k].para)
                            p.replace(old_name, copy_name)
                            new_clause.append(p)
                    if len(new_clause) == 1:
                        for k in range(len(clause_set)):
                            if len(clause_set[k]) == 1 and new_clause[0].para == clause_set[k][0].para:
                                key = -1
                                break
                    if key == -1:
                        continue
                    clause_set.append(new_clause)
                    msg = print_msg(key, i, j, old_name, copy_name)
                    print(msg + format_clause_for_output(new_clause))
                    if end_loop(new_clause, clause_set):  # 使用新函数判断是否结束
                        status = False
                        break
            else:
                for j in range(len(clause_set)):
                    key = -1
                    if i != j and len(clause_set[i]) == len(clause_set[j]):
                        for k in range(len(clause_set[i])):
                            if clause_set[i][k].para == clause_set[j][k].para:
                                continue
                            elif clause_set[i][k].get_name() == clause_set[j][k].get_name() and clause_set[i][k].para[1:] == clause_set[j][k].para[1:]:
                                if key != -1:
                                    key = -1
                                    break
                                key = k
                            else:
                                key = -1
                                break
                    if key == -1:
                        continue
                    new_clause = []
                    for k in range(len(clause_set[i])):
                        if k != key:
                            p = Predicate("")
                            p.copy(clause_set[j][k].para)
                            new_clause.append(p)
                    if len(new_clause) == 1:
                        for k in range(len(clause_set)):
                            if len(clause_set[k]) == 1 and new_clause[0].para == clause_set[k][0].para:
                                key = -1
                                break
                    if key == -1:
                        continue
                    clause_set.append(new_clause)
                    msg = print_msg(key, i, j, [], [])
                    print(msg + format_clause_for_output(new_clause))
                    if end_loop(new_clause, clause_set): 
                        status = False
                        break
        if not status:
            break

    print("Success!")

if __name__ == '__main__':
    main()
