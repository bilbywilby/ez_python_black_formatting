import csv
import logging
import os
from pathlib import Path
from typing import Dict, List


# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter and add to console handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(ch)


class Phonebook:
    def __init__(self, filename: str = 'phonebook.csv') -> None:
        """
        Initialize an instance of the Phonebook class.

        :param filename: The name of the csv file to use for storing contacts.
        """
        self.filename = filename
        self.contacts = self.load_contacts()

    def load_contacts(self) -> List[Dict[str, str]]:
        """
        Load existing contacts from the csv file.

        :return: A list of dictionaries representing each contact.
        """
        contacts = []
        if os.path.isfile(self.filename):
            with open(self.filename, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    contacts.append(row)
        return contacts

    def save_contacts(self) -> None:
        """
        Save the current contacts to the csv file.
        """
        with open(self.filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.contacts[0].keys())
            writer.writeheader()
            for contact in self.contacts:
                writer.writerow(contact)

    def search_contacts(self, search_term: str) -> List[Dict[str, str]]:
        """
        Search for contacts by name or phone number.

        :param search_term: The search term used to find matching contacts.
        :return: A list of all contacts that match the search term.
        """
        matching_contacts = []
        for contact in self.contacts:
            if search_term.lower() in contact['name'].lower() or search_term in contact['phone']:
                matching_contacts.append(contact)
        return matching_contacts

    def add_contact(self, name: str, phone: str) -> None:
        """
        Add a new contact to the phonebook.

        :param name: The name of the new contact.
        :param phone: The phone number of the new contact.
        """
        new_contact = {'name': name, 'phone': phone}
        self.contacts.append(new_contact)
        self.save_contacts()
        logger.info(f'New contact added: {name}, {phone}')

    def delete_contact(self, name: str) -> None:
        """
        Delete a contact from the phonebook.

        :param name: The name of the contact to delete.
        """
        for contact in self.contacts:
            if contact['name'] == name:
                self.contacts.remove(contact)
                self.save_contacts()
                logger.info(f'Contact deleted: {name}')
                break


if __name__ == '__main__':
    # Initialize logger
    logfile = Path(__file__).with_suffix('.log')
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.WARNING)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Create Phonebook
    phonebook = Phonebook()
    logger.info('Phonebook created')

    # Add contacts
    phonebook.add_contact('Alice', '555-1234')
    phonebook.add_contact('Bob', '555-5678')

    # Search contacts
    results = phonebook.search_contacts('alice')
    logger.debug(results)

    # Delete a contact
    phonebook.delete_contact('Bob')