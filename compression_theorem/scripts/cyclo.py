#!/usr/bin/env python3
"""
cyclo.py -- exact arithmetic in the cyclotomic field Q(zeta_L).

An element of Q(zeta_L) is represented as a sympy Poly in x over QQ, understood
modulo the L-th cyclotomic polynomial Phi_L(x).  Two such polys represent the
same algebraic number iff their remainders mod Phi_L are equal.  This gives an
EXACT equality test (no floating point) for the identities we need:

  * zeta_L^m               ->  Poly(x**(m mod L))            reduced mod Phi_L
  * A(k) = sum_i s_i zeta_L^{i k}
  * complex conjugation    ->  x -> x^{-1} = x^{L-1}         (i.e. exponent -> -e)

Only integer/rational coefficients occur, so this is fully rigorous.
"""
import sympy as sp

x = sp.symbols('x')


class Cyclo:
    """Cache of Phi_L for reuse."""
    _phi = {}

    @classmethod
    def phi(cls, L):
        if L not in cls._phi:
            cls._phi[L] = sp.Poly(sp.cyclotomic_poly(L, x), x, domain='QQ')
        return cls._phi[L]

    @classmethod
    def reduce(cls, coeffs, L):
        """coeffs: dict {exponent -> rational}.  Returns Poly reduced mod Phi_L."""
        expr = sp.Integer(0)
        for e, c in coeffs.items():
            if c == 0:
                continue
            expr += sp.Integer(0) + c * x ** (e % L)
        p = sp.Poly(expr, x, domain='QQ')
        return p.rem(cls.phi(L))

    @classmethod
    def dft_poly(cls, seq, k, L):
        """A(k) = sum_i seq_i zeta_L^{i k}  as reduced Poly mod Phi_L."""
        coeffs = {}
        for i, s in enumerate(seq):
            e = (i * k) % L
            coeffs[e] = coeffs.get(e, 0) + s
        return cls.reduce(coeffs, L)

    @classmethod
    def equals_integer(cls, poly, N, L):
        """Is the reduced Poly equal to the rational integer N?"""
        return (poly - sp.Poly(sp.Integer(N), x, domain='QQ')).is_zero

    @classmethod
    def polys_equal(cls, p1, p2):
        return (p1 - p2).is_zero
