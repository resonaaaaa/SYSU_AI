"""一阶逻辑的归结原理：将一阶逻辑公式转换为子句集，并使用归结规则进行推理。
每个归结步骤将会记录为一个字符串，以"R[子句1, 子句2]=归结字句" 的形式，最终输出所有的归结步骤。
字句集使用set存储，而每个字句使用tuple存储
test: {(A,~B,C),(B,~C),(~A,)}
todo：1.将输入转化为子句集；2.实现归结规则；3.记录归结步骤并输出
"""

def main():
    #字句集输入格式：{(A,~B,C),(x,y),(f(x),)}，字句均为析取式，字句间为合取式
    clause_set = set()
    clauses = []  # 保持子句插入顺序的列表，索引对应于步骤编号
    clause_str = input("请输入子句集：")
    clause_str = clause_str.strip("{}")
    clause_list = clause_str.split("),(")  # 按照"),("分割成单个子句
    print(clause_list)
    for clause in clause_list:
        clause = clause.strip("()")  # 去掉子句两端的括号
        literals_list = [lit.strip() for lit in clause.split(",") if lit.strip()]
        tup = tuple(literals_list)
        if tup not in clause_set:
            clauses.append(tup)
            clause_set.add(tup)

    print("输入的子句集为：", clauses)
    reduce_steps = []  # 存储归结步骤
    
    for idx, clause in enumerate(clauses):
        reduce_steps.append(f"{idx+1} {clause}")

    # 开始归结
    processed_pairs = set()  # 记录已处理的子句对
    while True:
        new_added = False
        # 遍历所有未处理的对子句对
        for i in range(len(clauses)):
            for j in range(i+1, len(clauses)):
                if (i, j) in processed_pairs:
                    continue
                processed_pairs.add((i, j))
                clause1 = clauses[i]
                clause2 = clauses[j]
                results, lit1_index, lit2_index = resolve(clause1, clause2)

                for new_clause in results:
                    if new_clause in clause_set:
                        continue
                    # 给新生成的子句一个新编号
                    new_index = len(clauses) + 1
                    reduce_steps.append(f"{new_index} R[{i+1}{lit1_index}, {j+1}{lit2_index}]={new_clause}")
                    clauses.append(new_clause)
                    clause_set.add(new_clause)
                    new_added = True
                    # 如果生成空子句，归结成功
                    if new_clause == ():
                        print("归结成功，生成空子句。")
                        print("归结步骤：")
                        for step in reduce_steps:
                            print(step)
                        return reduce_steps

        if not new_added:
            print("无法归结出空子句，归结失败。")
            break
                        
    print("归结步骤：")
    for step in reduce_steps:
        print(step)

def is_opposite(l1,l2):
    if l1.startswith("~") and l1[1:]==l2:
        return True
    if l2.startswith("~") and l2[1:]==l1:
        return True
    return False

def get_opposite(lit):
    if lit.startswith("~"):
        return lit[1:]
    else:
        return "~"+lit
    
def has_oppisite(clause):
    literals = set(clause)
    for lit in literals:
        if get_opposite(lit) in literals:
            return True
    return False

#归结
def resolve(clause1, clause2):
    results = set()
    # 找出所有互补文字对
    complements = [] 
    for idx1, lit1 in enumerate(clause1):
        for idx2, lit2 in enumerate(clause2):
            if is_opposite(lit1, lit2):
                complements.append((idx1, lit1, idx2, lit2))

    if not complements:
        return results, '', ''

    set1 = set(clause1)
    set2 = set(clause2)
    to_remove1 = set()
    to_remove2 = set()
    for idx1, lit1, idx2, lit2 in complements:
        to_remove1.add(lit1)
        to_remove2.add(lit2)

    
    new_clause_set = set1.union(set2) - to_remove1 - to_remove2

    if has_oppisite(new_clause_set):    #如果新子句中仍有互补文字对，则不添加该子句
        return results, '', ''

    results.add(tuple(sorted(new_clause_set)))

    letters = 'abcdefghijklmn'
    lit1_index = ''.join(letters[idx] for idx, lit in enumerate(clause1) if lit in to_remove1)
    lit2_index = ''.join(letters[idx] for idx, lit in enumerate(clause2) if lit in to_remove2)

    return results, lit1_index, lit2_index


if __name__ == "__main__":
    main()
