#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import pulp

def run():
    b = list(map(int, '-252214 -81442  -92467  577308  212159  -193866 -171461 -199801 563287  -106933 -15562  -11242  -227766'.split()))
    t = ['りそな', 'ゆうちょ', 'ゆうちょ', 'UFJ', 'ゆうちょ', 'UFJ', 'ジャパンネット', 'ゆうちょ', 'ゆうちょ', '三井住友', '三井住友', 'ゆうちょ', 'ゆうちょ']
    print(b)
    print(t)

    banks = {
        # for debug
        0: ('A', 500),
        1: ('A', 500),
        # actual data
        'ゆうちょ': ('B', 50000, 216, 432),
        'UFJ': ('B', 30000, 270, 432),
        'ジャパンネット': ('B', 30000, 172, 270),
        '三井住友': ('B', 30000, 216, 432),
        'りそな': ('A', 216)
    }
    N = len(b)
    M = 1000000 # max value
    problem = pulp.LpProblem('p', pulp.LpMinimize)

    # x(i,j) i->jの輸送額
    x = {}
    s = {}
    for i in range(N):
        for j in range(N):
            x[i, j] = pulp.LpVariable("x({},{})".format(i,j), 0, 2*M, pulp.LpInteger)
            s[i, j] = []

    # 条件1: 受け渡した総額が条件にあってること
    for i in range(N):
        problem += (sum(x[k,i] for k in range(N)) - sum(x[i,k] for k in range(N))) == b[i], "Constraint_{}".format(i)
    # 条件2: 自分自身に送るのはない
    for i in range(N):
        problem += x[i,i] == 0, "Constraint_self_{}".format(i)

    costs = []
    # 手数料の最小化
    for i in range(N):
        for j in range(N):
            # 同じ銀行？
            if t[i] == t[j]:
                pass
                # 条件もなく、コストも常に0
            # 違う銀行で、タイプA
            elif banks[t[i]][0] == 'A':
                A = banks[t[i]][1]
                # バイナリ変数 delta
                delta = pulp.LpVariable("delta({},{})".format(i,j), 0, 1, pulp.LpInteger)
                s[i,j].append(delta)
                # 条件 delta <= x(i,j) <= delta * M
                problem += (delta <= x[i,j]), "Constraint_A1_({},{})".format(i,j)
                problem += (x[i,j] <= delta * M), "Constraint_A2_({},{})".format(i,j)
                # コストは A*delta
                costs.append(A * delta)
            elif banks[t[i]][0] == 'B':
                T = banks[t[i]][1]
                A = banks[t[i]][2]
                B = banks[t[i]][3]
                # バイナリ変数 delta1, delta2
                delta1 = pulp.LpVariable("delta1({},{})".format(i,j), 0, 1, pulp.LpInteger)
                delta2 = pulp.LpVariable("delta2({},{})".format(i,j), 0, 1, pulp.LpInteger)
                s[i,j].append(delta1)
                s[i,j].append(delta2)
                # 条件0 delta1 + delta2 <= 1
                problem += (delta1 + delta2 <= 1), "Constraint_B0_({},{})".format(i,j)
                # 条件1 delta1 + T*delta2 <= x(i,j) <= (T-1)*delta1 + M*delta2
                problem += (delta1 + T*delta2 <= x[i,j]), "Constraint_B1_({},{})".format(i,j)
                problem += (x[i,j] <= (T-1)*delta1 + M*delta2), "Constraint_B2_({},{})".format(i,j)
                # コストは A*delta1 + B*delta2
                costs.append(A * delta1)
                costs.append(B * delta2)
    # 目的関数の設定
    problem += sum(costs), "Objective"

    result = problem.solve()

    # 結果表示
    print('status', pulp.LpStatus[result])
    print('value', pulp.value(problem.objective))
    for i in range(N):
        for j in range(N):
            print(i, '->', j, pulp.value(x[i,j]), end=' ')
            if len(s[i,j]) == 1:
                print([pulp.value(s[i,j][0]) * banks[t[i]][1]])
            elif len(s[i,j]) == 2:
                print([pulp.value(s[i,j][0]) * banks[t[i]][2], pulp.value(s[i,j][1]) * banks[t[i]][3]])
            else:
                print([0])
run()
