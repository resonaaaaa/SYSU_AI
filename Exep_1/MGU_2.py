
import re


class Predicate:
    def __init__(self, in_str: str):
        s = in_str.strip()
        self.neg = False
        if s.startswith("~"):
            self.neg = True
            s = s[1:]
        if "(" in s and s.endswith(")"):
            self.name = s.split("(")[0]
            params = s[len(self.name) + 1:-1]
            self.para = [p.strip() for p in params.split(",")] if params else []
        else:
            self.name = s
            self.para = []

    def is_neg(self):
        return self.neg

    def get_pred_str(self):
        return ("~" if self.neg else "") + self.name + ("(" + ",".join(self.para) + ")" if self.para else "")

    def is_opposite(self, other):
        return self.name == other.name and self.neg != other.neg

    def rename_vars(self, subst: dict):
        for i, p in enumerate(self.para):
            if p in subst:
                self.para[i] = subst[p]


class Clause:
    def __init__(self, literals_list=None):
        self.literals = []
        if literals_list:
            for lit in literals_list:
                self.literals.append(Predicate(lit))

    def print_clause(self):
        if not self.literals:
            return "()"
        if len(self.literals) == 1:
            return self.literals[0].get_pred_str()
        return "(" + ",".join(l.get_pred_str() for l in self.literals) + ")"


# 变量：单字符小写字母 u..z
def is_var(x: str) -> bool:
    return re.match(r"^[u-z]$", x) is not None


def MGU(p1: Predicate, p2: Predicate):
    if p1.name != p2.name or len(p1.para) != len(p2.para):
        return None
    subst = {}
    for a, b in zip(p1.para, p2.para):
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


def apply_subst_clause(clause: Clause, subst: dict):
    for lit in clause.literals:
        lit.rename_vars(subst)


def resolve(c1: Clause, c2: Clause):
    results = []
    for i, l1 in enumerate(c1.literals):
        for j, l2 in enumerate(c2.literals):
            if l1.is_opposite(l2):
                subst = MGU(l1, l2)
                if subst is None:
                    continue
                new_literals = []
                for k, oth in enumerate(c1.literals):
                    if k != i:
                        new_literals.append(Predicate(oth.get_pred_str()))
                for k, oth in enumerate(c2.literals):
                    if k != j:
                        new_literals.append(Predicate(oth.get_pred_str()))
                new_clause = Clause([])
                new_clause.literals = new_literals
                apply_subst_clause(new_clause, subst)
                # 去重并检查矛盾
                strs = set()
                unique = []
                bad = False
                for lit in new_clause.literals:
                    s = lit.get_pred_str()
                    if s in strs:
                        continue
                    if any(lit.is_opposite(o) for o in new_clause.literals):
                        bad = True
                        break
                    strs.add(s)
                    unique.append(lit)
                if bad:
                    continue
                new_clause.literals = unique
                results.append((new_clause, i, j, subst))
    return results


def clause_convert(clause: Clause):
    return tuple(l.get_pred_str() for l in clause.literals)


def is_empty_clause(clause: Clause):
    return len(clause.literals) == 0


def parse_input_clause_set(in_str: str):
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

    clauses = []
    for cs in clause_strs:
        lits = split_literals(cs)
        clauses.append(Clause(lits))
    return clauses


def canonicalize_clause(clause: Clause):
    var_map = {}
    next_var = 0
    parts = []
    for lit in clause.literals:
        params = []
        for p in lit.para:
            if is_var(p):
                if p not in var_map:
                    var_map[p] = f"?{next_var}"
                    next_var += 1
                params.append(var_map[p])
            else:
                params.append(p)
        parts.append((lit.name, lit.neg, tuple(params)))
    return tuple(parts)


def is_tautology_clause(clause: Clause):
    seen = set()
    for lit in clause.literals:
        seen.add((lit.name, tuple(lit.para), lit.neg))
    for name, params, neg in [(x[0], x[1], x[2]) for x in seen]:
        if (name, params, not neg) in seen:
            return True
    return False


def is_subsumed(canonical_new, visited_canonicals):
    new_set = set((n, neg, params) for (n, neg, params) in canonical_new)
    for exist in visited_canonicals:
        exist_set = set((n, neg, params) for (n, neg, params) in exist)
        if exist_set.issubset(new_set):
            return True
    return False


def resolution_step(clause_list: list):
    steps = []
    clause_list_copy = clause_list[:]
    visited = set()
    visited_canonicals = []
    clause_map = {id(clause_list_copy[k]): k + 1 for k in range(len(clause_list_copy))}
    next_idx = len(clause_list_copy) + 1

    for idx, c in enumerate(clause_list_copy, start=1):
        steps.append((idx, clause_convert(c)))
        canon = canonicalize_clause(c)
        visited.add(canon)
        visited_canonicals.append(canon)

    unit_queue = [c for c in clause_list_copy if len(c.literals) == 1]
    general_queue = [c for c in clause_list_copy if len(c.literals) != 1 and c not in unit_queue]
    to_process = unit_queue + general_queue
    processed = []
    processed_pairs = set()

    while to_process:
        c1 = to_process.pop(0)
        processed.append(c1)
        for c2 in clause_list_copy + processed:
            if c1 is c2:
                continue
            pair_id = (id(c1), id(c2))
            if pair_id in processed_pairs:
                continue
            processed_pairs.add(pair_id)

            res = resolve(c1, c2)
            for new_clause, i, j, subst in res:
                if is_tautology_clause(new_clause):
                    continue

                canon = canonicalize_clause(new_clause)
                if is_subsumed(canon, visited_canonicals):
                    continue

                if canon in visited:
                    continue

                visited.add(canon)
                visited_canonicals.append(canon)
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
                meta = f"R[{label1},{label2}]{{{sub_str}}}"
                steps.append((meta, next_idx))
                if is_empty_clause(new_clause):
                    return steps
                next_idx += 1
    return steps


def main():
    in_str = input("请输入子句集（例如：{On(tony,mike),(~On(x,y),Green(y))}）：\n")
    clauses = parse_input_clause_set(in_str)
    for c in clauses:
        print(c.print_clause())

    steps = resolution_step(clauses)

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
    main()

