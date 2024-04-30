#!/usr/bin/python

import sympy as sp
import sys
import re
import math

def simple_iterations_method_for_system_2(func1, func2, intervals, epsilon):
    n = 1
    state = 1
    x1_sym = sp.symbols('x_1')
    x2_sym = sp.symbols('x_2')

    lm_1 = sp.symbols('lambda_1')
    lm_2 = sp.symbols('lambda_2')

    x_1_lower_bound, x_1_upper_bound = intervals[0]
    x_2_lower_bound, x_2_upper_bound = intervals[1]

    start_expr_1 = func1(x1_sym, x2_sym)
    start_expr_2 = func2(x1_sym, x2_sym)

    phi_1 = x1_sym + lm_1 * start_expr_1
    phi_2 = x2_sym + lm_2 * start_expr_2

    s_e_1_diff_x1 = sp.diff(start_expr_1, x1_sym)
    s_e_1_diff_x2 = sp.diff(start_expr_1, x2_sym)
    s_e_1_diff_G = [s_e_1_diff_x1.subs(x1_sym, x_1_lower_bound).subs(x2_sym, x_2_lower_bound),
                    s_e_1_diff_x1.subs(x1_sym, x_1_lower_bound).subs(x2_sym, x_2_upper_bound),
                    s_e_1_diff_x1.subs(x1_sym, x_1_upper_bound).subs(x2_sym, x_2_lower_bound),
                    s_e_1_diff_x1.subs(x1_sym, x_1_upper_bound).subs(x2_sym, x_2_upper_bound),
                    s_e_1_diff_x2.subs(x1_sym, x_1_lower_bound).subs(x2_sym, x_2_lower_bound),
                    s_e_1_diff_x2.subs(x1_sym, x_1_lower_bound).subs(x2_sym, x_2_upper_bound),
                    s_e_1_diff_x2.subs(x1_sym, x_1_upper_bound).subs(x2_sym, x_2_lower_bound),
                    s_e_1_diff_x2.subs(x1_sym, x_1_upper_bound).subs(x2_sym, x_2_upper_bound)]
    lm_phi_1 = max(s_e_1_diff_G)
    phi_1 = phi_1.subs(lm_1, -1 / lm_phi_1)

    s_e_2_diff_x1 = sp.diff(start_expr_2, x1_sym)
    s_e_2_diff_x2 = sp.diff(start_expr_2, x2_sym)
    s_e_2_diff_G = [
        s_e_2_diff_x1.subs(x1_sym, x_1_lower_bound).subs(x2_sym, x_2_lower_bound),
        s_e_2_diff_x1.subs(x1_sym, x_1_lower_bound).subs(x2_sym, x_2_upper_bound),
        s_e_2_diff_x1.subs(x1_sym, x_1_upper_bound).subs(x2_sym, x_2_lower_bound),
        s_e_2_diff_x1.subs(x1_sym, x_1_upper_bound).subs(x2_sym, x_2_upper_bound),
        s_e_2_diff_x2.subs(x1_sym, x_1_lower_bound).subs(x2_sym, x_2_lower_bound),
        s_e_2_diff_x2.subs(x1_sym, x_1_lower_bound).subs(x2_sym, x_2_upper_bound),
        s_e_2_diff_x2.subs(x1_sym, x_1_upper_bound).subs(x2_sym, x_2_lower_bound),
        s_e_2_diff_x2.subs(x1_sym, x_1_upper_bound).subs(x2_sym, x_2_upper_bound)
    ]
    lm_phi_2 = max(s_e_2_diff_G)
    phi_2 = phi_2.subs(lm_2, -1 / lm_phi_2)

    if (
            (
                abs(sp.diff(phi_1, x1_sym).subs(x1_sym, x_1_upper_bound - epsilon).subs(x2_sym, x_2_upper_bound - epsilon)) +
                abs(sp.diff(phi_1, x2_sym).subs(x2_sym, x_2_upper_bound - epsilon).subs(x1_sym, x_1_upper_bound - epsilon)) < 1
            )
            and
            (
                abs(sp.diff(phi_2, x1_sym).subs(x1_sym, x_1_upper_bound - epsilon).subs(x2_sym, x_2_upper_bound - epsilon)) +
                abs(sp.diff(phi_2, x2_sym).subs(x2_sym, x_2_upper_bound - epsilon).subs(x1_sym, x_1_upper_bound - epsilon)) < 1
            )
    ):
        state = 1

    else:
        state = 0

    x1_prev = x_1_upper_bound
    x2_prev = x_2_upper_bound

    x1_cur = phi_1.subs(x1_sym, x1_prev).subs(x2_sym, x2_prev)
    x2_cur = phi_2.subs(x1_sym, x1_prev).subs(x2_sym, x2_prev)

    while abs(x1_cur - x1_prev) > epsilon or abs(x2_cur - x2_prev) > epsilon:
        x1_prev = x1_cur
        x1_cur = phi_1.subs(x1_sym, x1_prev).subs(x2_sym, x2_prev)

        x2_prev = x2_cur
        x2_cur = phi_2.subs(x1_sym, x1_prev).subs(x2_sym, x2_prev)
        n += 1

        # print(n, float(x1_cur), float(x2_cur))

        if n > 50:
            state = -1

    

    return [[float(x1_cur), float(x2_cur)],
            [start_expr_1.subs(x1_sym, x1_cur).subs(x2_sym, x2_cur),
             start_expr_2.subs(x1_sym, x1_cur).subs(x2_sym, x2_cur)], n, state]


text_func_1 = sys.argv[1]
text_func_2 = sys.argv[2]

def replaceCharacters(string):
    string = string.replace(' ', '')
    string = string.replace('^', '**')
    pattern = r'tg\((.*?)\)'
    string = re.sub(pattern, r'sp.tan(\1)', string)
    pattern = r'ctg\((.*?)\)'
    string = re.sub(pattern, r'cot.tan(\1)', string)
    pattern = r'ln\((.*?)\)'
    string = re.sub(pattern, r'cot.tan(\1)', string)
    pattern = r'cos\((.*?)\)'
    string = re.sub(pattern, r'sp.cos(\1)', string)
    pattern = r'sin\((.*?)\)'
    string = re.sub(pattern, r'sp.sin(\1)', string)
    return string

text_func_1 = replaceCharacters(text_func_1)
text_func_2 = replaceCharacters(text_func_2)



func1 = lambda x, y: x + y
exec(f"func1 = lambda x, y: {text_func_1}")

func2 = lambda x, y: x + y
exec(f"func2 = lambda x, y: {text_func_2}")


intervals = [[float(sys.argv[3]), float(sys.argv[4])], [float(sys.argv[5]), float(sys.argv[6])]]
epsilon = float(sys.argv[7])

print(simple_iterations_method_for_system_2(func1, func2, intervals, epsilon))
