import pyplot_tools
import matplotlib.pyplot as plt
import numpy as np
from pyfinance import ExpenseType, CurrencyType


def plot_expenses_by_type(expense_items):
    """
    show expense of each week and breakdown by type as stacked bar chart
    x axis is week, y axis is money spent
    """
    weeks = []
    expenses_by_type = {}
    for et in ExpenseType:
        # initialize dictionary
        expenses_by_type[et.name] = []

    for expense_item in expense_items:
        # todo: this does not work when year changes
        week = expense_item.date.isocalendar()[1]
        try:
            week_index = weeks.index(week)
        except ValueError:
            # week is not in list yet
            weeks.append(week)
            for et in ExpenseType:
                expenses_by_type[et.name].append(0)
            week_index = len(weeks) - 1
        expense_type = expense_item.type.name
        expenses_by_type[expense_type][week_index] += expense_item.getConvertedValue(CurrencyType.CHF)
    
    # plot as stacked bar chart
    fig, ax = plt.subplots()
    pyplot_tools.format_figure(ax)
    bottom = np.zeros(len(weeks))
    for et in ExpenseType:
        if et in [ExpenseType.INCOME, ExpenseType.TRANSFER, ExpenseType.TO_BE_REIMBURSED]:
            continue
        data = expenses_by_type[et.name]
        plt.bar(weeks, data, label=et.name, bottom=bottom)
        bottom += data
    plt.legend()
    plt.title("Expenses by type")
    plt.xlabel("Week")
    plt.ylabel("Amount")
    plt.show()
        
