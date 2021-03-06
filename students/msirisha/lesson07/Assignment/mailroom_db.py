from peewee import *
from mailroom_donor_report import print_donor_report
from create_mailroom_db import Donor, Donation


def first_name(name):
    """
    :param name: Donor name
    :return: Return first name
    """
    name_split = name.split()
    if len(name_split) >= 1:
        return name_split[0]

def last_name(name):
    """
    :param name: Donor name
    :return: return last name
    """

    name_split = name.split()
    if len(name_split) == 1:
        return ''
    else:
        return ''.join(name_split[1:])

def generate_letter(name):
        """ Generate letter for donor """
        format_string =  "Dear {first_name} {last_name},\n \nThank you for your generous donation ${last_donation:.2f}." \
                         "\n \n\n\t\tSincerely, \n\t\tLocal Charity"

        query = (Donor
                 .select(Donor.name, Donor.last, Donor.first, fn.MAX(Donation.id).alias('last_don_id'), Donation.amount)
                 .join(Donation, JOIN.LEFT_OUTER)
                 )
        result = None
        for d in query:
            result = format_string.format(
                last_donation=float(d.donation.amount),
                first_name=d.first,
                last_name=d.last
            )

        return result


def send_thank_you_menu(database):
    """
    Sends thank you message for the donors. Prompts for donor name, if not present, adds Donor to data.
    Prompts for donation and adds it to donor's data. Prints a 'Thank You' email populated with the donor's data.
    :return: None
    """

    while True:
        name = input("Enter a Full Name ('list' to show list of donors, 'q' to quit): ")
        if name == 'q' or name == '':
            return
        elif name == 'list':
            database.connect()
            database.execute_sql('PRAGMA foreign_keys = ON;')
            for d in Donor.select(Donor.name):
                print(d.name)
            database.close()
            continue
        else:
            try:
                database.connect()
                database.execute_sql('PRAGMA foreign_keys = ON;')
                with database.transaction():
                    new_donor = Donor.create(name=name, first=first_name(name), last=last_name(name))
                    new_donor.save()

            except IntegrityError as e:
                print("Donor already exists, adding donations to existing donor.")

            finally:
                database.close()

            break

    while True:
        try:
            amount = float(input(f"Enter a donation amount for {name} : "))
            if amount <= 0:
                print('Amount donated must be a positive number.')
            else:
                break
        except ValueError:
            print('Please enter a numerical value.')

    database.connect()
    database.execute_sql('PRAGMA foreign_keys = ON;')
    with database.transaction():
        new_donation = Donation.create(donor=name, amount=amount)
        new_donation.save()
    database.close()

    print(generate_letter(name))


def menu(menu_data):
    """
        Prints the main user menu & retrieves user selection.
    :param: a menu list, consisting of iterable with three values:
        [0]: text to be presented to user
        [1]: function that should be called for the menu item
        [2]: parameter that should be used in the function call, None if no parameter call needed
    :return: two values:
        1) the function corresponding to the user's selection, or None on a bad selection
        raises ValueError if choice is non-numeric
        2) a parameter that should be used with the fn call, None if no parameter needed
    """
    print("\nPlease choose one of the following options:")

    for index, menu_item in enumerate(menu_data):   # Prints the menu user text
        print(f"{index + 1}) {menu_item[0]}")

    choice = int(input("> ")) - 1

    if choice in range(len(menu_data)):                     # Ensure that option chosen is within menu range, this
        return menu_data[choice][1], menu_data[choice][2]   # handles choosing 0, which would return menu_data[-1][1]

    return None


if __name__ == "__main__":

    database = SqliteDatabase('./mailroom.db')

    menu_functions = [
        ('Send a Thank You', send_thank_you_menu, database),
        ('Print a report', print_donor_report, database),
        ('Quit', exit, None),
    ]
    while True:
        try:
            menu_fn, param = menu(menu_functions)
            if param:
                menu_fn(param)
            else:
                menu_fn()
        except TypeError:
            continue
        except ValueError:
            continue