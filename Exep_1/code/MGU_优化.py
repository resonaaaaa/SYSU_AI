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

class ResNode:
    """二叉树节点，记录子句索引与父节点索引（用于检测祖先关系以避免冗余配对）"""
    def __init__(self, idx, parent1=None, parent2=None):
        self.idx = idx
        self.parent1 = parent1
        self.parent2 = parent2


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
    # 使用文字索引建立映射
    literal_index = {}
    #建立一个子句ID与索引的映射表
    clause_map = {id(clause_list_copy[k]): k + 1 for k in range(len(clause_list_copy))}
    next_idx = len(clause_list_copy) + 1

    # 建立二叉树节点映射,用索引标识节点
    clause_nodes = {}
    for k in range(len(clause_list_copy)):
        clause_nodes[k+1] = ResNode(k+1, None, None)

    #将初始子句加入步骤列表
    for idx, c in enumerate(clause_list_copy, start=1):
        steps.append((idx, clause_convert(c)))
        formatted = format_clause(c) 
        visited.add(formatted)
        visited_clause_list.append(formatted)
        # 更新文字索引
        for lit in formatted:
            key = (lit[0], lit[1])
            literal_index.setdefault(key, set()).add(formatted)
        # 记录每个索引对应的规范化表示，供祖先比较使用
        clause_canonical_by_index = locals().get('clause_canonical_by_index', {})
        clause_canonical_by_index[idx] = formatted
        # 保存在外部变量
        clause_canonical_by_index = clause_canonical_by_index

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
            # 使用格式化子句标识，避免不同对象但等价子句的重复配对
            try:
                pid1 = format_clause(c1)
                pid2 = format_clause(c2)
            except Exception:
                pid1 = clause_convert(c1)
                pid2 = clause_convert(c2)
            pair_id = tuple(sorted((pid1, pid2)))  #标识处理过的子句对，避免重复处理
            if pair_id in processed_pairs:
                continue
            processed_pairs.add(pair_id)

            # 跳过祖先-后代的配对
            idx1 = clause_map.get(id(c1))
            idx2 = clause_map.get(id(c2))
            def is_ancestor(a_idx, b_idx):
                # 检查 a_idx 是否是 b_idx 的祖先
                if a_idx is None or b_idx is None:
                    return False
                stack = [b_idx]
                visited = set()
                while stack:
                    cur = stack.pop()
                    if cur is None or cur in visited:
                        continue
                    visited.add(cur)
                    node = clause_nodes.get(cur)
                    if node is None:
                        continue
                    if node.parent1 == a_idx or node.parent2 == a_idx:
                        return True
                    if node.parent1:
                        stack.append(node.parent1)
                    if node.parent2:
                        stack.append(node.parent2)
                return False

            if idx1 is not None and idx2 is not None and (is_ancestor(idx1, idx2) or is_ancestor(idx2, idx1)):
                continue

            res = resolve(c1, c2)   #产生新子句，获取新子、消掉的文字索引和替换字典
            for new_clause, i, j, subst in res: 
                if has_paradox(new_clause): #矛盾子句跳过
                    continue

                # 格式化子句并检查是否与任一祖先重复
                formatted = format_clause(new_clause)
                # 使用文字索引做包含检测：
                new_set = set((n, neg, params) for (n, neg, params) in formatted)
                # 找出候选已访问子句
                candidate_sets = []
                for lit in formatted:
                    key = (lit[0], lit[1])
                    candidate_sets.append(literal_index.get(key, set()))
                if candidate_sets:
                    candidates = set.intersection(*candidate_sets) if len(candidate_sets) > 1 else set(candidate_sets[0])
                else:
                    candidates = set(visited_clause_list)

                # 检查是否有已访问子句包含 new_clause并跳过
                skip_due_to_superset = False
                to_remove = []
                for v in list(candidates):
                    exist_set = set((n, neg, params) for (n, neg, params) in v)
                    if exist_set.issubset(new_set):
                        # 已访问子句更小（包含性），说明 new 被包含，跳过
                        skip_due_to_superset = True
                        break
                    if new_set.issubset(exist_set):
                        # new 更小，移除被 new 覆盖的已访问子句
                        to_remove.append(v)
                if skip_due_to_superset:
                    continue
                for v in to_remove:
                    try:
                        visited.remove(v)
                    except KeyError:
                        pass
                    try:
                        visited_clause_list.remove(v)
                    except ValueError:
                        pass
                    # 从 literal_index 中移除
                    for lit in v:
                        key = (lit[0], lit[1])
                        if key in literal_index:
                            literal_index[key].discard(v)

                # 获取祖先函数
                def get_ancestors(idx):
                    res = set()
                    stack = [idx]
                    while stack:
                        cur = stack.pop()
                        if cur is None or cur in res:
                            continue
                        res.add(cur)
                        node = clause_nodes.get(cur)
                        if not node:
                            continue
                        if node.parent1:
                            stack.append(node.parent1)
                        if node.parent2:
                            stack.append(node.parent2)
                    return res

                anc1 = get_ancestors(idx1) if idx1 is not None else set()
                anc2 = get_ancestors(idx2) if idx2 is not None else set()
                ancestors = anc1.union(anc2)
                # 检查祖先中是否已有相同的规范化表示
                duplicate_in_ancestors = False
                for a in ancestors:
                    if a in clause_canonical_by_index and clause_canonical_by_index[a] == formatted:
                        duplicate_in_ancestors = True
                        break
                if duplicate_in_ancestors:
                    continue
                if is_subsumed(formatted, visited_clause_list ):  #被已访问的子句包含了，说明新子句没有有效信息，跳过
                    continue

                if formatted in visited:  #访问过的子句跳过
                    continue

                # 将 new_clause 加入已访问并更新文字索引
                visited.add(formatted)
                visited_clause_list .append(formatted)
                for lit in formatted:
                    key = (lit[0], lit[1])
                    literal_index.setdefault(key, set()).add(formatted)
                clause_list_copy.append(new_clause)
                # 若新子句为单文字则优先处理，放到队列最前面
                if len(new_clause.literals) == 1:
                    to_process.insert(0, new_clause)
                else:
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
                # 在二叉树中记录新节点及其父节点索引
                clause_nodes[next_idx] = ResNode(next_idx, idx1, idx2)
                # 记录该节点的规范化表示，便于祖先比较
                clause_canonical_by_index[next_idx] = formatted

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
    default_input = "{(A(tony),),(A(mike),),(A(john),),(L(tony, rain),),(L(tony, snow),),(~A(x), S(x), C(x)),(~C(y), ~L(y, rain)),(L(z, snow), ~S(z)),(~L(tony, u), ~L(mike, u)),(L(tony, v), L(mike, v)),(~A(w), ~C(w), S(w))}"
    in_str = input(f"请输入子句集或使用默认输入(Alpine Club)：") or default_input
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

