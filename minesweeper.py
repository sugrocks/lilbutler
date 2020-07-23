# Code based on https://gist.github.com/mohd-akram/3057736
# From this idea https://www.reddit.com/r/shitcord/comments/am0bzf/liking_the_new_minesweeper_update_so_far/
import random

from discord.ext import commands
from botutils import del_message
from string import ascii_lowercase


class Minesweeper(commands.Cog):
    """Minesweeper generator with spoilers!"""

    def __init__(self, bot):
        self.bot = bot
        print('| Loaded:   minesweeper')

    def setupgrid(self, gridsize, start, numberofmines):
        emptygrid = [['0' for i in range(gridsize)] for i in range(gridsize)]

        for i, j in self.getmines(emptygrid, start, numberofmines):
            emptygrid[i][j] = 'X'

        grid = self.getnumbers(emptygrid)

        return grid

    def showgrid(self, grid):
        gridsize = len(grid)

        horizontal = '   ' + (4 * gridsize * '-') + '-'

        # Print top column letters
        toplabel = '     '

        for i in ascii_lowercase[:gridsize]:
            toplabel = toplabel + i + '   '

        print(toplabel + '\n' + horizontal)

        # Print left row numbers
        for idx, i in enumerate(grid):
            row = '{0:2} |'.format(idx + 1)

            for j in i:
                row = row + ' ' + j + ' |'

            print(row + '\n' + horizontal)

        print('')

    def getrandomcell(self, grid):
        gridsize = len(grid)

        a = random.randint(0, gridsize - 1)
        b = random.randint(0, gridsize - 1)

        return (a, b)

    def getneighbors(self, grid, rowno, colno):
        gridsize = len(grid)
        neighbors = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                elif -1 < (rowno + i) < gridsize and -1 < (colno + j) < gridsize:
                    neighbors.append((rowno + i, colno + j))

        return neighbors

    def getmines(self, grid, start, numberofmines):
        mines = []
        neighbors = self.getneighbors(grid, *start)

        for i in range(numberofmines):
            cell = self.getrandomcell(grid)
            while cell == start or cell in mines or cell in neighbors:
                cell = self.getrandomcell(grid)
            mines.append(cell)

        return mines

    def getnumbers(self, grid):
        for rowno, row in enumerate(grid):
            for colno, cell in enumerate(row):
                if cell != 'X':
                    # Gets the values of the neighbors
                    values = [grid[r][c] for r, c in self.getneighbors(grid, rowno, colno)]

                    # Counts how many are mines
                    grid[rowno][colno] = str(values.count('X'))

        return grid

    def showcells(self, grid, currgrid, rowno, colno):
        # Exit function if the cell was already shown
        if currgrid[rowno][colno] != ' ':
            return

        # Show current cell
        currgrid[rowno][colno] = grid[rowno][colno]

        # Get the neighbors if the cell is empty
        if grid[rowno][colno] == '0':
            for r, c in self.getneighbors(grid, rowno, colno):
                # Repeat function for each neighbor that doesn't have a flag
                if currgrid[r][c] != 'F':
                    self.showcells(grid, currgrid, r, c)

    @commands.command(description='Create a grid')
    async def minesweeper(self, ctx, size: int = 9, mines: int = 0):
        """
        Don't blow up!
        If you don't set a number of mines, it will pick randomly between `size` and `size * 2`.
        """
        try:
            if size < 0:
                await ctx.send('Sorry %s, but the grid has to be a positive number.' % ctx.message.author.mention)
            if size > 13:
                await ctx.send('Sorry %s, but max size is 13.' % ctx.message.author.mention)
            elif size == 0:
                await ctx.send('I can\'t make a grid without any cells, %s!' % ctx.message.author.mention)
            elif size == 1:
                if random.randint(0, 1) == 1:
                    out = '\n||:bomb:||'
                else:
                    out = '\n||:clap:||'

                await ctx.send('Here\'s your coin toss, %s! %s' % (ctx.message.author.mention, out))
                await del_message(self, ctx)
            else:
                # await self.bot.send_typing(ctx.message.channel)

                if mines == 0:
                    mines = random.randint(size - 1, size * 2 - 1)

                if mines < 1:
                    await ctx.send('Sorry %s, but I need at least one mine.' % ctx.message.author.mention)
                    return
                elif mines > 80:
                    await ctx.send('Sorry %s, but over 80 mines is too much.' % ctx.message.author.mention)
                    return

                start = (
                    random.randint(1, size + 1),
                    random.randint(1, size + 1)
                )

                grid = self.setupgrid(size, start, mines)

                out = ''
                for line in grid:
                    out += '\n' + ''.join(line)

                out = (out.replace('X', '||:bomb:||')
                          .replace('0', '||:zero:||')
                          .replace('1', '||:one:||')
                          .replace('2', '||:two:||')
                          .replace('3', '||:three:||')
                          .replace('4', '||:four:||')
                          .replace('5', '||:five:||')
                          .replace('6', '||:six:||')
                          .replace('7', '||:seven:||')
                          .replace('8', '||:height:||'))

                await ctx.send('%s - %dx%d - %dx:bomb: %s' % (ctx.message.author.mention, size, size, mines, out))
                await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR minesweeper ', e)


def setup(bot):
    bot.add_cog(Minesweeper(bot))
