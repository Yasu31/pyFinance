import sys
sys.path.append('../')
from pyFinance import pyFinance, visualizer

pyFinance.addNewItemsToDatabase()
pyFinance.addLabelsToDatabase()
expense_items = pyFinance.loadExpenseItems()
visualizer.plot_expenses_by_type(expense_items)
