from pyFinance import pyplot_tools
from pyFinance.pyFinance import ExpenseType, CurrencyType
import matplotlib.pyplot as plt
import numpy as np
from datetime import date

class BinningType:
    WEEK = 1
    MONTH = 2


def plot_expenses_by_type(expense_items, binning_type=BinningType.WEEK, img_filename=None):
    """
    show expense of each week and breakdown by type as stacked bar chart
    x axis is week, y axis is money spent
    visualization could be wrong if negative expense items are present
    """
    bins = []
    bin_names = []  # readable bin names (week or month name)
    expenses_by_type = {}  # expenses_by_type[ExpenseType.HOGE] = [sum for bin 1, ...]
    for et in ExpenseType:
        # initialize dictionary
        expenses_by_type[et.name] = []

    for expense_item in expense_items:
        week = expense_item.date.isocalendar()[1]
        month = expense_item.date.month
        year = expense_item.date.year
        # get readable week name
        start_date = date.fromisocalendar(year, week, 1)
        if binning_type == BinningType.WEEK:
            # get unique week ID for indexing
            unique_id = (start_date - date(2020, 1, 1)).days // 7
        elif binning_type == BinningType.MONTH:
            unique_id = month + year * 12

        try:
            if binning_type == BinningType.WEEK:
                index = bins.index(unique_id)
            elif binning_type == BinningType.MONTH:
                index = bins.index(unique_id)
        except ValueError:
            # this bin is not in list yet
            bins.append(unique_id)
            
            if binning_type == BinningType.WEEK:
                bin_names.append(f"{start_date} ~")
            elif binning_type == BinningType.MONTH:
                bin_names.append(f"{year}-{month}")

            for et in ExpenseType:
                expenses_by_type[et.name].append(0)
            index = len(bins) - 1
        expense_type = expense_item.type.name
        expenses_by_type[expense_type][index] += expense_item.getConvertedValue(CurrencyType.CHF)
    
    # plot latest 10 bins
    bins = bins[-10:]
    bin_names = bin_names[-10:]
    for et in ExpenseType:
        expenses_by_type[et.name] = expenses_by_type[et.name][-10:]
    
    # plot as stacked bar chart
    fig, ax = plt.subplots()
    pyplot_tools.format_figure(ax)
    bottom = np.zeros(len(bins))
    hatch_pattern = ['', '//', '..', '++', 'xx']
    i = 0
    for et in ExpenseType:
        if et in [ExpenseType.INCOME, ExpenseType.TRANSFER, ExpenseType.TO_BE_REIMBURSED]:
            continue
        data = expenses_by_type[et.name]
        plt.xticks(bins, bin_names, rotation=45, ha="right")
        plt.bar(bins, data, label=et.name, bottom=bottom, hatch=hatch_pattern[i % len(hatch_pattern)])
        bottom += data
        i += 1
    plt.legend()
    plt.title("Expenses by type")
    plt.xlabel("Week" if binning_type == BinningType.WEEK else "Month")
    plt.ylabel("Amount [CHF]")
    if img_filename is not None:
        assert img_filename.endswith(".png")
        plt.savefig(img_filename)
    else:
        plt.show()
        
