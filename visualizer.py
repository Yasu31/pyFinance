import pyplot_tools
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
from pyfinance import ExpenseType, CurrencyType


def plot_expenses_by_type(expense_items):
    """
    show expense of each week and breakdown by type as stacked bar chart
    x axis is week, y axis is money spent
    todo: feedback most expensive purchase every week by type
    """
    weeks = []
    week_names = []  # readable week names
    expenses_by_type = {}  # expenses_by_type[ExpenseType.HOGE] = [sum for week 1, ...]
    for et in ExpenseType:
        # initialize dictionary
        expenses_by_type[et.name] = []

    for expense_item in expense_items:
        week = expense_item.date.isocalendar()[1]
        year = expense_item.date.isocalendar()[0]
        # get readable week name
        start_date = date.fromisocalendar(year, week, 1)
        # get unique week ID for indexing
        unique_week_id = (start_date - date(2020, 1, 1)).days // 7

        try:
            week_index = weeks.index(unique_week_id)
        except ValueError:
            # week is not in list yet
            weeks.append(unique_week_id)
            
            week_names.append(f"{start_date} ~")

            for et in ExpenseType:
                expenses_by_type[et.name].append(0)
            week_index = len(weeks) - 1
        expense_type = expense_item.type.name
        expenses_by_type[expense_type][week_index] += expense_item.getConvertedValue(CurrencyType.CHF)
    
    # plot as stacked bar chart
    fig, ax = plt.subplots()
    pyplot_tools.format_figure(ax)
    bottom = np.zeros(len(weeks))
    hatch_pattern = ['', '//', '..', '++', 'xx']
    i = 0
    for et in ExpenseType:
        if et in [ExpenseType.INCOME, ExpenseType.TRANSFER, ExpenseType.TO_BE_REIMBURSED]:
            continue
        data = expenses_by_type[et.name]
        plt.xticks(weeks, week_names)
        plt.bar(weeks, data, label=et.name, bottom=bottom, hatch=hatch_pattern[i % len(hatch_pattern)])
        bottom += data
        i += 1
    plt.legend()
    plt.title("Expenses by type")
    plt.xlabel("Week")
    plt.ylabel("Amount [CHF]")
    plt.show()
        
