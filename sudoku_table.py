import math

action_number = 0
round_number = 0


def get_square_num(row_num, column_num):
    return math.floor((column_num + 3) / 3) + math.floor(row_num / 3) * 3


class Table:

    def __init__(self):
        self.table = []
        fp = input('Enter the table\'s path: ')
        with open(fp, 'r') as f:
            table = f.read()  # f.write(table)
        table = table.replace('\n', '')
        table = table.split('/')
        for i in range(len(table)):
            table[i] = table[i].split('|')
        self.table = table

    def set_table(self, table):
        self.table = table

    def __copy__(self) -> object:
        temp = Table()

        for row_inx in range(9):
            temp.table[row_inx] = self.table[row_inx].copy()

        return temp

    def __str__(self):
        st = '| '
        for row_num in range(9):
            for triplet_num in range(3):
                for in_triplet in range(3):
                    st += self.table[row_num][triplet_num * 3 + in_triplet] + ' '
                st += '| '

            if (row_num + 1) % 3 == 0:
                st += '\n-------------------------\n| '
            else:
                st += '\n| '

        return st[:-3]

    def get_row(self, num) -> list:
        return self.table[num]

    def get_column(self, num) -> list:
        lst = []
        for i in range(9):
            lst.append(self.table[i][num])
        return lst

    def get_square(self, num):
        """

        :param num: The square's number - 1 is the upper left, 9 is the lower right
        :return:
        """

        row = math.floor((num - 1) / 3) * 3
        column = ((num % 3) - 1) * 3
        lst = []
        for i in range(3):
            sub_row = self.get_row(row + i)
            for j in range(3):
                lst.append(sub_row[column + j])

        return lst

    def add_num(self, row_num, column_num, num):
        self.table[row_num][column_num] = num

    def try_num(self, row_num, column_num, num):
        square_num = get_square_num(row_num, column_num)
        if num in self.get_row(row_num) or num in self.get_column(column_num) or num in self.get_square(square_num):
            return False
        return True

    def detect_missing(self, something_num: int, something: str):
        if something == 'row':
            something = self.get_row(something_num)
        elif something == 'column':
            something = self.get_column(something_num)
        else:
            something = self.get_square(something_num)

        missing = []
        missing_inx = []
        for num in range(1, 10):
            if str(num) not in something:
                missing.append(num)
            if something[num - 1] == ' ':
                missing_inx.append(num - 1)
        return missing, missing_inx

    def in_something(self, something_num: int, something: str):
        is_row: bool = something == 'row'
        is_column: bool = something == 'column'
        temp = self.detect_missing(something_num, something)
        missing = temp[0]
        missing_inx = temp[1]
        del temp
        for num in missing:
            options = []
            for inx in missing_inx:
                if (is_row and self.try_num(something_num, inx, str(num))) or (
                        is_column and self.try_num(inx, something_num, str(num))):
                    options.append(inx)
                else:
                    row_inx = math.floor(inx / 3) + math.floor((something_num - 1) / 3) * 3
                    column_inx = inx % 3 + ((something_num + 2) % 3) * 3
                    if self.try_num(row_inx, column_inx, str(num)):
                        options.append(inx)

                if len(options) > 1:
                    break

            if len(options) == 1:
                if is_row:
                    self.add_num(something_num, options[0], str(num))
                elif is_column:
                    self.add_num(options[0], something_num, str(num))
                else:
                    possible_row = math.floor(options[0] / 3) + math.floor((something_num - 1) / 3) * 3
                    possible_column = options[0] % 3 + ((something_num + 2) % 3) * 3
                    self.add_num(possible_row, possible_column, str(num))
                global action_number
                action_number += 1
                missing.remove(num)
                missing_inx.remove(options[0])

    def best_guess(self, req=2):
        good_q = []

        for inx in range(9):  # Searches for the row/column with the lowest number of missing numbers
            temp = self.detect_missing(inx, 'row')
            missing = temp[0]

            if len(missing) == req:
                for i in temp[1]:
                    good_q.append(((inx, i), missing))

            temp = self.detect_missing(inx, 'column')
            missing = temp[0]

            if len(missing) == req:
                for i in temp[1]:
                    good_q.append(((i, inx), missing))

            temp = self.detect_missing(inx + 1, 'square')
            missing = temp[0]
            if len(missing) == req:
                for i in temp[1]:
                    row = math.floor(i / 3) + math.floor(inx / 3) * 3
                    column = i % 3 + ((inx + 3) % 3) * 3
                    good_q.append(((row, column), missing))
        return good_q

    def guess(self, req):
        guess = self.best_guess(req)
        while len(guess) == 0:
            req += 1
            guess = self.best_guess(req)
        return guess

    def random_cheating(self):
        req = 2
        guess = self.guess(req)
        while len(guess) == 0:
            req += 1
            guess = self.best_guess(req)
        for option_in_guess in range(len(guess)):
            for the_guessed_number in range(req):
                safe_copy = self.__copy__()

                self.add_num(guess[option_in_guess][0][0], guess[option_in_guess][0][1],
                             str(guess[option_in_guess][1][the_guessed_number]))
                if self.solve():
                    print('SOLVED!\n', self, sep='')
                    return
                self = safe_copy.__copy__()

    def single_round(self):
        global round_number
        for i in range(9):
            self.in_something(i, 'row')
            self.in_something(i, 'column')
            self.in_something(i + 1, 'square')
        round_number += 9

    def solve(self):
        while not self.finished():
            for i in range(3):
                self.single_round()

            copy = self.__copy__()
            self.single_round()
            if not self.finished() and self.table == copy.table:
                return False
        return True

    def finished(self):
        for row in self.table:
            if ' ' in row:
                return False
        return True


if __name__ == '__main__':
    t = Table()
    print('FIRST \n', t, sep='')
    t.solve()
    if t.finished():
        print('SOLVED!\n', t, sep='')
    else:
        t.random_cheating()

if __name__ == '__main__':
    t = Table()