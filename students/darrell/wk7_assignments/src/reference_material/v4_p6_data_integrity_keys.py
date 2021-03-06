"""
    Learning persistence with Peewee and sqlite
    delete the database file to start over
        (but running this program does not require it)

        data integrity keys
"""

from peewee import *
from src.v00_personjob_model import Person, Job, PersonNumKey

import logging


def add_with_without_bk():
    """
        demonstrate impact of business keys
    """

    person_name = 0
    lives_in_town = 1
    nickname = 2
    people = [
        ('Andrew', 'Sumner', 'Andy'),
        ('Peter', 'Seattle', None),
        ('Susan', 'Boston', 'Beannie'),
        ('Pam', 'Coventry', 'PJ'),
        ('Steven', 'Colchester', None),
    ]

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    database = SqliteDatabase('../data/personjob.db')

    logger.info('Try creating Person records again: it will fail')

    try:
        database.connect()
        database.execute_sql('PRAGMA foreign_keys = ON;')
        try:
            with database.transaction():
                for person in people:
                    new_person = Person.create(
                        person_name = person[person_name],
                        lives_in_town = person[lives_in_town],
                        nickname = person[nickname])
                    new_person.save()
                    logger.info('Database add successful')

        except Exception as e:
            logger.info(f'Error creating = {person[person_name]}')
            logger.info(e)

        logger.info('We make sure duplicates are not unintentionally created this way')
        logger.info('BUT: how do we really identify a Person (uniquely)?')

        logger.info('Creating Person records, but in a new table with generated PK...')
        try:
            with database.transaction():
                for person in people:
                    new_person = PersonNumKey.create(
                        person_name = person[person_name],
                        lives_in_town = person[lives_in_town],
                        nickname = person[nickname])
                    new_person.save()

        except Exception as e:
            logger.info(f'Error creating = {person[0]}')
            logger.info(e)

        logger.info('Watch what happens when we do it again')

        try:
            with database.transaction():
                for person in people:
                    new_person = PersonNumKey.create(
                        person_name = person[person_name],
                        lives_in_town = person[lives_in_town],
                        nickname = person[nickname])
                    new_person.save()

        except Exception as e:
            logger.info(f'Error creating = {person[0]}')
            logger.info(e)

        logger.info('Note no PK specified, no PK violation; "duplicates" created!')
        for person in PersonNumKey.select():
            logger.info(f'Name : {person.person_name} with id: {person.id}')

    except Exception as e:
        logger.info(e)

    finally:
        database.close()


if __name__ == '__main__':
    add_with_without_bk()
