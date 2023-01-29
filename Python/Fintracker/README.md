Fintracker
==========

Fintracker, or personal finance tracker, features a CLI menu for managing personal finances.
It allows for the registration of expenses and revenue on a database, and provides the ability to display or remove these transactions.
The script also includes functionality for scheduling recurring transactions, such as rent and wages, and the ability export transactions to a CSV file.
Every transaction can have a note, and the expenses must have a category.

It is possible to generate charts of the transactions (revenue or expenses), and also of the percentages of expenses by category.
It also offers a summary of recent transactions, a net result and a balance statement.

Besides that, it features a balance statement that can be edited, allowing for the creation of a different transaction type known as a balance transaction.
Every transaction, whether an expense or revenue, affects the balance's cash.
The script also includes the functionality to correct the balance when removing transactions from the database, and also prevents/warns the user about negative balance items.
Also, for example, if the user attempts to increase the value of "stock positions" by € 1,000.00 with his "savings", while only having € 500.00 available, it will suggest to increase the "stock positions" value by € 500.00, and leave the "savings" at € 0.00, or to cancel the operation.

This script is just a showcase of my python abilities. I don't use it.
