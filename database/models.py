from peewee import *

db = SqliteDatabase("drugs.db")

class Reciept(Model):
    user = CharField(verbose_name="Айди пользователя")
    listname = CharField(verbose_name="Название списка")

    class Meta:
        database = db

class Drugs(Model):
    name = CharField(max_length=100)
    info = CharField()

    class Meta:
        database = db

class RecieptItem(Model):
    drug = CharField()
    reciept = ForeignKeyField(Reciept, backref="recieptitems")

    class Meta:
        database = db


def prepare_database():
    db.connect()
    db.create_tables([Drugs])


