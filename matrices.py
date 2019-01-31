from math import sqrt, pi, ceil, cos, sin, log10
from numbers import Number

from fraction import Fraction


class Matrix(list):
    """
    A matrix. A list of equal-length columns.
    """
    nrows: int
    ncols: int

    def __init__(self, rows: [[], ]):
        """
        Requires that all elements of m
        are lists of equal length.
        """
        self.nrows = len(rows)
        self.ncols = len(rows[0])
        super().__init__([Vector(row) for row in rows])

    def is_square(self):
        return self.nrows is self.ncols

    def __iadd__(self, other):
        """
        Requires that all respective elements of self
        and other are instances of the same type.
        """
        # check if matrix addition is valid
        if isinstance(other, Matrix):
            if not (other.nrows is self.nrows and
                    other.ncols is self.ncols):
                raise MatrixSizeError('dimensions not equal')
            for r in range(self.nrows):
                for c in range(self.ncols):
                    self[r][c] += other[r][c]
        else:
            return NotImplemented

    def __add__(self, other):
        """
        Requires that all respective elements of self
        and other are instances of the same type.
        """
        # check if matrix addition is valid
        if isinstance(other, Matrix):
            if not (other.nrows is self.nrows and
                    other.ncols is self.ncols):
                raise MatrixSizeError('dimensions not equal')
            sum_mtx = []
            for r in range(self.nrows):
                sum_mtx.append(
                    [self[r][c] + other[r][c]
                     for c in range(self.ncols)]
                )
            return Matrix(sum_mtx)
        else:
            return NotImplemented

    def transpose(self):
        """Reflection of entries along the main diagonal."""
        t = []
        for c in range(self.ncols):
            t.append([self[r][c] for r in
                      range(self.nrows)])
        return Matrix(t)

    def det(self) -> (Fraction, None):
        """Returns the determinant of this matrix if it is square."""
        if self.is_square():
            rows = list(range(self.nrows))
            cols = list(range(self.ncols))
            return self.__det(rows, cols)
        else:
            raise MatrixSizeError('matrix not square.')

    def __det(self, rows: [int, ], cols: [int, ]) -> Fraction:
        """
        Private helper for det(). Recursive function.
        cols and rows are chopped up index slices.
        """
        # Terminating condition:
        if len(rows) is 1:  # implies len(rows) is 1
            return self[rows[0]][cols[0]]
        else:
            det = 0.0
            for i in range(len(cols)):
                _cols = cols.copy()
                _cols.remove(i)
                _det = self[cols[i]][rows[0]]
                _det *= self.__det(rows[1:], _cols)
                if i % 2 is 1:
                    _det *= -1
                det += _det
            return det

    def reduce(self):
        pass  # TODO:

    def inverse(self):
        if not self.is_square():
            return
        pass  # TODO

    def __mul__(self, other):
        """
        Returns the matrix multiplication of
        self and other, if it is valid.
        (Ie. a matrix if other is a matrix,
             a vector if other is a vector,
             None if
        """
        # Matrix multiplied be another matrix:
        if isinstance(other, Matrix):
            if self.ncols is not other.nrows:
                raise MatrixSizeError('op1 #cols != op2 #rows')
            prod = []
            other_t = other.transpose()
            for r in range(self.nrows):
                prod.append(
                    [sum(self[r].dot(c))
                     for c in other_t]
                )
            return Matrix(prod)

        # Matrix multiplied by a vector:
        elif isinstance(other, Vector):
            if self.ncols is not len(other):
                raise MatrixSizeError('op1 #cols != op2 length')
            return Vector([
                sum(self[r].dot(other))
                for r in range(self.nrows)
            ])

        # Unexpected second operand:
        else:
            return NotImplemented

    # TODO: fix after refactor
    def __rmul__(self, other):
        """
        Multiplies this matrix by a leading scalar.
        Returns the product.
        """
        if isinstance(other, Number):
            m = []
            for c in range(self.ncols):
                m.append([e * other for e in self[c]])
            return Matrix(m)
        else:
            return NotImplemented

    def __str__(self):
        s = ''
        max_numer = max(map(lambda c: max(c.__numer_val), self))
        max_denom = max(map(lambda c: max(c.__denom_val), self))
        width = int(ceil(log10(max_numer))) + \
            int(ceil(log10(max_denom)))

        for row in self:
            rs = ', '.join(map(
                lambda v: ('%1.2s' % str(v))
                .center(width + 2), row)
            )
            s += '[%s]\n' % rs
        return s


class MatrixSizeError(Exception):
    """
    Used to raise Arithmetic exceptions when
    operand matrix sizes are incompatible.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Vector(list):
    """
    A vector. All entries are Fraction objects.
    """

    def __init__(self, v: list):
        """
        Requires that all elements of v
        are Numbers. Initialize self with
        the fraction versions of v's entries.
        """
        v = [Fraction(n) for n in v]
        super().__init__(v)

    def norm(self):
        """ Returns the 'length' of the vector. """
        # Equivalent to sqrt(sum(self.dot(self))):
        return sqrt(sum(map(lambda x: x ** 2, self)))

    def rot(self, o, axis=''):
        """
        Returns a rotated view of a vector in space.
        The rotation is counterclockwise by theta,
        about the specified axis when relevant.
        """
        rm = {  # TODO: Make this an external dictionary/lambda
            2: {
                '': Matrix([[cos(o), -sin(o)],
                            [sin(o), cos(o)]])
            },
            3: {
                'x': Matrix([[1, 0, 0],
                             [0, cos(o), -sin(o)],
                             [0, sin(o), cos(o)]]),
                'y': Matrix([[cos(o), 0, sin(o)],
                             [0, 1, 0],
                             [-sin(o), 0, cos(o)]]),
                'z': Matrix([[cos(o), -sin(o), 0],
                             [sin(o), cos(o), 0],
                             [0, 0, 1]])
            }
        }  # Rotation matrices based on size
        if len(self) not in rm.keys():
            return
        if o < 0:
            o = ceil(-o / 2 / pi) * 2 * pi + o
        o %= 2 * pi
        return rm[len(self)][axis] * self

    def transform(self):
        """Return a [1 x len(self)] matrix"""
        return Matrix(self)

    def dot(self, other):
        """
        If the vectors are of equal vector length,
        Returns the dot product of this and other.
        """
        if (isinstance(other, Vector) and
                len(self) is len(other)):
            prod = [self[i] * other[i] for i in range(len(self))]
            return Vector(prod)
        else:
            raise MatrixSizeError('vector lengths incompatible.')

    def __mul__(self, other):
        """Vector cross product."""
        if (isinstance(other, Vector) and
                len(self) is 3 and
                len(self) is len(other)):
            mtx = [[1, -1, 1], self[0], other[0]]
            cross = []  # TODO
            return Vector(cross)
        else:
            raise MatrixSizeError('not vectors of length 3.')

    def __rmul__(self, other):
        if isinstance(other, Fraction):
            return Vector([
                other * entry for entry in self
            ])
        elif isinstance(other, Number):
            f_other = Fraction(other)
            return Vector([
                f_other * entry for entry in self
            ])
        else:
            return NotImplemented


vec = Vector([0, 1, 2, 3])
mtx = Matrix([[0, 11],  # [0, 11]
              [2, 3]])  # [2,  3]
frac = Fraction(1)
print(frac.numer, frac.denom)
print(vec)
print(str(5 * vec))
print(str(2 * mtx * mtx))
print((2 * mtx * mtx).det(), 44 * 62 - 66 * 12)
