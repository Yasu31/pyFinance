import pyfinance
import visualizer

pyfinance.addNewItemsToDatabase()
pyfinance.addLabelsToDatabase()
expense_items = pyfinance.loadExpenseItems()
visualizer.plot_expenses_by_type(expense_items)
