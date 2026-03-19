def main():
    #字句集输入格式：{(A,~B,C),(x,y),(f(x),)}，字句均为析取式，字句间为合取式
    clause_set = set()
    clause_str= input("请输入子句集：")
    clause_str = clause_str.strip("{}")  # 去掉外层的大括号
    clause_list = clause_str.split("),(")  # 按照"),("分割成单个子句
    print(clause_list)
    for clause in clause_list:
        clause = clause.strip("()")  # 去掉子句两端的括号
        

    print("输入的子句集为：", clause_set) 


if __name__ == "__main__":    main()
