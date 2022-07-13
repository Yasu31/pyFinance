import pandas
import numpy as np
from enum import Enum, auto
from datetime import datetime
import os


class CurrencyType(Enum):
    JPY = 'jpy'
    CHF = 'chf'


class ExpenseType(Enum):
    """
    TWINT payments from friends should be counted as expense for whatever that pays for.
    """
    RESTAURANT = 'r'
    GROCERY = 'g'
    TRANSPORTATION = 't'
    INCOME = 'i'  # in which case this is not counted as an expense
    OTHER = 'o'
    UNSORTED = 'u'


class ExpenseItem:
    def __init__(self, date, description, expense_type, amount, currency_type, comment=""):
        assert isinstance(date, datetime)
        self.date = date
        assert isinstance(description, str)
        self.description = description
        assert isinstance(expense_type, ExpenseType)
        self.type = expense_type
        assert isinstance(amount, float)
        self.amount = amount
        assert isinstance(currency_type, CurrencyType)
        self.currency = currency_type
        assert isinstance(comment, str)
        self.comment = comment
    
    def askExpenseType(self):
        print(f"what type of expense is \"{self.description}\" on {self.date}, costing {self.amount} {self.currency}?")
        options = ""
        for i, expense_type in enumerate(ExpenseType):
            options += f"{i}: {expense_type.name} ({expense_type.value})\n"
        print(options)
        choice = input()
        while True:
            try:
                self.type = ExpenseType(choice)
                break
            except ValueError:
                print("invalid choice, try again")
                choice = input()


def generateExpenseItemsFromRawCSV(filename):
    # generate a list of ExpenseItem objects from a CSV file
    # type and comment fields are not filled
    # todo: this only supports credit suisse CSV formats
    with open(filename, 'r') as f:
        # data begins from 4th row
        data = pandas.read_csv(f, skiprows=5)
    expense_items = []
    for index, row in data.iterrows():
        date_string = row['Booking Date']
        description = row['Text']
        try:
            date = datetime.strptime(date_string, '%d.%m.%Y')
        except ValueError:
            print(f"Error: date \"{date_string}\" is not in correct format for item \"{description}\", skipping")
            continue

        debit = float(row['Debit'])
        if np.isnan(debit):
            debit = 0.
        credit = float(row['Credit'])
        if np.isnan(credit):
            credit = 0.
        amount = debit - credit
        
        expense_item = ExpenseItem(date, description, ExpenseType.UNSORTED, amount, CurrencyType.CHF)
        expense_items.append(expense_item)
    return expense_items


def loadExpenseItems():
    """
    load expense items already registered in the designated CSV format in expense_database.csv
    """
    expense_items = []
    if not os.path.isfile('expense_database.csv'):
        print("expense_database.csv not found")
        return expense_items 
    
    with open('expense_database.csv', 'r') as f:
        data = pandas.read_csv(f)
    for index, row in data.iterrows():
        date_string = row['date']
        date = datetime.strptime(date_string, '%Y-%m-%d')
        description = row['description']
        expense_type = ExpenseType(row['type'])
        amount = float(row['amount'])
        currency = CurrencyType(row['currency'])
        comment = str(row['comment'])
        expense_item = ExpenseItem(date, description, expense_type, amount, currency, comment)
        expense_items.append(expense_item)
    return expense_items


def saveExpenseItems(expense_items):
    """
    save list of expense items to expense_database.csv
    """
    with open('expense_database.csv', 'w') as f:
        # use pandas
        data = pandas.DataFrame(columns=['date', 'description', 'type', 'amount', 'currency', 'comment'])
        for expense_item in expense_items:
            data.loc[len(data)] = [expense_item.date, expense_item.description, expense_item.type.value, expense_item.amount, expense_item.currency.value, expense_item.comment]
        data.to_csv(f, index=False)


def addNewItemsToDatabase():
    """
    find raw CSVs, go through them and add new expenses found to the database.
    """
    expense_database = loadExpenseItems()

    # find raw CSVs (CSVs downloaded from whatever bank or credit card)
    raw_csvs = []
    for filename in os.listdir():
        if filename.endswith('.csv') and not filename == 'expense_database.csv':
            raw_csvs.append(filename)
    print(f"found CSV files: {raw_csvs}")

    # go through raw CSVs and add new items to the database
    new_expense_items = []
    for filename in raw_csvs:
        new_expense_item_candidates = generateExpenseItemsFromRawCSV(filename)
        for new_expense_item_candidate in new_expense_item_candidates:
            # check that this does not exist in the database already
            is_new_flag = True
            for e in expense_database:
                if e.date == new_expense_item_candidate.date and e.description == new_expense_item_candidate.description and e.amount == new_expense_item_candidate.amount and e.currency == new_expense_item_candidate.currency:
                    # type and comment are input by user and not loaded from file, so don't check for those
                    is_new_flag = False
                    break
            if is_new_flag:
                new_expense_items.append(new_expense_item_candidate)
        print(f"found {len(new_expense_items)} new items in {filename}")
    expense_database.extend(new_expense_items)
    saveExpenseItems(expense_database)


def addLabelsToDatabase():
    """
    ask user for labels for each expense item
    """
    expense_database = loadExpenseItems()
    for expense_item in expense_database:
        if expense_item.type == ExpenseType.UNSORTED:
            expense_item.askExpenseType()
    saveExpenseItems(expense_database)
