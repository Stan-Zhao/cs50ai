import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=20):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
    
    def __hash__(self):
        return hash((frozenset(self.cells), self.count))

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells   
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count-=1


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """

        # 1) 记录已经点击的安全单元格
        self.moves_made.add(cell)

        # 2) 记录为安全单元
        self.mark_safe(cell)

        # 3) 生成新的句子
        new_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (0 <= i < self.height and 0 <= j < self.width and (i, j) != cell):
                    if (i, j) not in self.safes and (i, j):
                        new_cells.add((i, j))

        # 处理已知的雷
        known_mines = sum(1 for (i, j) in new_cells if (i, j) in self.mines)
        count -= known_mines
        new_cells -= self.mines  # 去掉已知的雷

        if new_cells:
            self.knowledge.append(Sentence(new_cells, count))
        # 5) 句子推理：创建新句子
        inferred_sentences = []
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 != s2 and s1.cells.issubset(s2.cells):
                    new_sentence = Sentence(s2.cells - s1.cells, s2.count - s1.count)
                    if new_sentence not in self.knowledge and new_sentence not in inferred_sentences:
                        inferred_sentences.append(new_sentence)

        self.knowledge += inferred_sentences
        # 4) 不断更新知识，直到不再有新的信息
        while True:  
            safes_to_mark = set()
            mines_to_mark = set()

            for sentence in self.knowledge:
                safes_to_mark.update(sentence.known_safes())
                mines_to_mark.update(sentence.known_mines())

            if not safes_to_mark and not mines_to_mark:
                break  

            for safe_cell in safes_to_mark:
                self.mark_safe(safe_cell)

            for mine_cell in mines_to_mark:
                self.mark_mine(mine_cell)


        # 6) 清理知识库
        self.knowledge = [s for s in self.knowledge if s.cells]  # 删除空句子



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe_cell in self.safes:
            if safe_cell not in self.moves_made:
                return safe_cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines, and
            3) are not part of any knowledge statements (to avoid uncertainty)
        """
        all_cells = set(itertools.product(range(self.height), range(self.width)))
        knowledge_cells = set()

        # 收集所有 knowledge 里涉及的点
        for sentence in self.knowledge:
            knowledge_cells.update(sentence.cells)

        # 过滤掉已知地雷、已选点，以及 knowledge 里涉及的点
        possible_cells = all_cells - self.moves_made - self.mines - knowledge_cells

        if possible_cells:
            return random.choice(list(possible_cells))
        
        # 如果 `possible_cells` 为空，则尝试从所有未选过的非雷点中选择
        fallback_cells = all_cells - self.moves_made - self.mines
        if fallback_cells:
            return random.choice(list(fallback_cells))

        # 所有格子都已选过或者是雷，没有可选的格子
        return None
