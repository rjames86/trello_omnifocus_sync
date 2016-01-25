"""

tell front document of application "OmniFocus"
    set theProject to the container of the first flattened task where its id = "maYU0s1ENwO"
    set theContainer to the modification date of the first flattened project where its id = (id of theProject)
end tell

"""

from subprocess import Popen, PIPE
from peewee import (
    Model,
    CharField,
    DateTimeField,
    BooleanField,
    BlobField,
)
from playhouse.sqlite_ext import SqliteExtDatabase
from dateutil import parser as dateparser

db = SqliteExtDatabase('my_database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Omnifocus(BaseModel):
    task_id = CharField(),
    name = CharField()
    parent = CharField(),
    creation_date = DateTimeField(),
    modification_date = DateTimeField(),
    completed = BooleanField()

    @classmethod
    def create_new(cls, task_id, name, parent, creation_date, modification_date, completed):
        task = cls.create(
            task_id=task_id,
            name=name,
            parent=parent,
            creation_date=dateparser.parse(creation_date),
            modification_date=dateparser.parse(modification_date),
            completed=completed
        )
        task.save()
        return task


class OmnifocusTasks(object):
    # TODO(ryan) make this work with projects
    TASK_TEMPLATE = """
    tell front document of application "OmniFocus"
        set theProject to first flattened project where its name = "{project_name}"
        tell theProject to make new task with properties {properties}
    end tell
    """

    PROJECT_TEMPLATE = """
    tell front document of application "Omnifocus"
        tell (folder named "Trello" of folder named "Dropbox")
            make new project with properties {properties}
        end tell
    end tell
    """

    @classmethod
    def make_project(cls, project_name):
        properties = dict(name=project_name)
        cls._communicate(cls.PROJECT_TEMPLATE, properties)


    @classmethod
    def add_task(cls, project_name, name, *args, **kwargs):
        properties = dict(name=name)
        for key, value in kwargs.iteritems():
            properties[key] = value
        cls._communicate(cls.TASK_TEMPLATE, properties, project_name=project_name)

    @classmethod
    def _format_property_string(cls, d):
        key_values = ", ".join(['%s: "%s"' % item for item in d.iteritems()])
        return "{%s}" % key_values

    @classmethod
    def _communicate(cls, template, properties, *args, **kwargs):
        p = Popen(["osascript", "-"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        print template.format(properties=cls._format_property_string(properties), **kwargs)
        print p.communicate(template.format(properties=cls._format_property_string(properties), **kwargs))
