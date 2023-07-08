import pandas
import numpy as np
from enum import Enum, auto
from datetime import datetime
import os
import re


class CurrencyType(Enum):
    JPY = 'jpy'
    CHF = 'chf'
    EUR = 'eur'
    GBP = 'gbp'


class DataSourceType(Enum):
    WISE_JPY = 'wisejpy'
    WISE_CHF = 'wisechf'
    WISE_EUR = 'wiseeur'
    CSX = 'csx'
    NEON = 'neon'


class ExpenseType(Enum):
    """
    TWINT payments from friends should be counted as expense for whatever that pays for.
    DO NOT change the values of the enum members as they are used in the database.
    """
    RESTAURANT = 'r'
    GROCERY = 'g'
    TRANSPORTATION = 'tp'
    INCOME = 'i'  # in which case this is not counted as an expense
    COMMUNICATIONS = 'c'
    ADMINISTRATIVE = 'a'  # tax, city registration fee, etc
    RENT = 'rent'
    HOUSEHOLD = 'h'  # non-food items for daily use
    INSURANCE = 'in'  # health insurance etc
    PARTY = 'p'  # for home parties
    ENTERTAINMENT = 'e'  # sightseeing, movies, games, etc.
    HOTEL = 'ht'  # hotel stays
    TRANSFER = 'tf'  # transferring money between my accounts. Not counted as expense
    TO_BE_REIMBURSED = 'tbr'  # will be reimbursed by the lab, so don't count as expense
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
            options += f"{expense_type.value}: {expense_type.name}\n"
        print(options)
        choice = input()
        while True:
            try:
                self.type = ExpenseType(choice)
                break
            except ValueError:
                print("invalid choice, try again")
                choice = input()
    
    def getConvertedValue(self, currency_type):
        # todo: use API to get actual conversion rate
        if self.currency == currency_type:
            return self.amount
        if currency_type == CurrencyType.CHF and self.currency == CurrencyType.JPY:
            return self.amount / 140.
        if currency_type == CurrencyType.CHF and self.currency == CurrencyType.EUR:
            return self.amount * 1.
        if currency_type == CurrencyType.CHF and self.currency == CurrencyType.GBP:
            return self.amount * 1.13
        raise NotImplementedError(f"conversion from {self.currency} to {currency_type} not implemented")


def generateExpenseItemsFromRawCSV(filename):
    # generate a list of ExpenseItem objects from a CSV file
    # type fields are not filled

    # determine the data source type from the filename
    if re.search('[0-9]{7}-[0-9]+_Bookings_[0-9]{2}-[0-9]{2}-[0-9]{4}.csv', filename):
        datasource_type = DataSourceType.CSX
    elif re.search('statement_[0-9]+_JPY_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}-[0-9]{2}-[0-9]{2}.csv', filename):
        datasource_type = DataSourceType.WISE_JPY
    elif re.search('statement_[0-9]+_CHF_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}-[0-9]{2}-[0-9]{2}.csv', filename):
        datasource_type = DataSourceType.WISE_CHF
    elif re.search('statement_[0-9]+_EUR_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}-[0-9]{2}-[0-9]{2}.csv', filename):
        datasource_type = DataSourceType.WISE_EUR
    elif re.search('[0-9]{4}_account_statements.csv', filename):
        datasource_type = DataSourceType.NEON
    else:
        raise NotImplementedError(f"datasource type for {filename} not implemented")
    print(f"loading {filename} as {datasource_type}")

    with open(filename, 'r') as f:
        skiprows = 0
        sep = ','
        if datasource_type == DataSourceType.CSX:
            # data begins from 6th row
            skiprows = 5
        if datasource_type == DataSourceType.NEON:
            sep = ';'
        data = pandas.read_csv(f, skiprows=skiprows, sep=sep)
    expense_items = []
    for index, row in data.iterrows():
        if datasource_type == DataSourceType.CSX:
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
        elif datasource_type == DataSourceType.WISE_JPY or datasource_type == DataSourceType.WISE_CHF or datasource_type == DataSourceType.WISE_EUR:
            date_string = row['Date']
            description = row['Description']
            try:
                date = datetime.strptime(date_string, '%d-%m-%Y')
            except ValueError:
                print(f"Error: date \"{date_string}\" is not in correct format for item \"{description}\", skipping")
                continue
            amount = -float(row['Amount'])
            comment = f"merchant: {row['Merchant']}, Wise ID: {row['TransferWise ID']}, Note: {row['Note']}, total fees: {row['Total fees']}"
            if datasource_type == DataSourceType.WISE_JPY:
                currency_type = CurrencyType.JPY
                assert 'JPY' == row['Currency']
            elif datasource_type == DataSourceType.WISE_EUR:
                currency_type = CurrencyType.EUR
                assert 'EUR' == row['Currency']
            else:
                currency_type = CurrencyType.CHF
                assert 'CHF' == row['Currency']
            expense_item = ExpenseItem(date, description, ExpenseType.UNSORTED, amount, currency_type, comment)
        
        elif datasource_type == DataSourceType.NEON:
            date_string = row['Date']
            description = row['Description']
            comment = row['Subject']
            if type(comment) != str:
                comment = ""
            amount = -float(row['Amount'])
            # add implementation if needed
            assert np.isnan(row["Original amount"])
            assert np.isnan(row["Original currency"])
            assert np.isnan(row["Exchange rate"])
            assert row["Wise"] == "no"
            try:
                date = datetime.strptime(date_string, '%Y-%m-%d')
            except ValueError:
                print(f"Error: date \"{date_string}\" is not in correct format for item \"{description}\", skipping")
                continue
            expense_item = ExpenseItem(date, description, ExpenseType.UNSORTED, amount, CurrencyType.CHF, comment)
            
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
    save list of expense items to expense_database.csv ordered by date
    """
    with open('expense_database.csv', 'w') as f:
        # use pandas
        columns = ['date', 'description', 'type', 'amount', 'currency', 'comment']
        data = pandas.DataFrame(columns=columns)
        for expense_item in expense_items:
            data.loc[len(data)] = [expense_item.date, expense_item.description, expense_item.type.value, expense_item.amount, expense_item.currency.value, expense_item.comment]
        # using the column entries to sort will make sure output has same order every single time
        data.sort_values(by=columns, inplace=True)
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
            # do some hardcoded guessing
            grocery_keys = ["Migros", "Coop"]
            transport_keys = ["SBB"]
            restaurant_keys = ["Orient Catering", "Uzh Zentrum", "Sv (schweiz) Ag"]
            if any(key in expense_item.description for key in grocery_keys) or any(key in expense_item.comment for key in grocery_keys):
                expense_item.type = ExpenseType.GROCERY
            elif any(key in expense_item.description for key in transport_keys) or any(key in expense_item.comment for key in transport_keys):
                expense_item.type = ExpenseType.TRANSPORTATION
            elif any(key in expense_item.description for key in restaurant_keys) or any(key in expense_item.comment for key in restaurant_keys):
                expense_item.type = ExpenseType.RESTAURANT
            else:
                expense_item.askExpenseType()
    saveExpenseItems(expense_database)
