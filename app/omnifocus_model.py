from peewee import *
from peewee import _BaseFormattedField, _date_part
from subprocess import Popen, PIPE
from playhouse.sqlite_ext import SqliteExtDatabase

import datetime
import re

database = SqliteDatabase('/Users/rjames/Library/Containers/com.omnigroup.OmniFocus2/Data/Library/Caches/com.omnigroup.OmniFocus2/OmniFocusDatabase2', **{})


db = SqliteExtDatabase('omnifocus_trello.db')


class OmnifocusTrello(Model):
    '''
    Keeps track of Trello Card ID -> Omnifocus Task ID
    '''
    class Meta:
        database = db

    trello_id = CharField(unique=True)
    omnifocus_id = CharField(unique=True)

    def __init__(self, *args, **kwargs):
        super(OmnifocusTrello, self).__init__(self, *args, **kwargs)
        if not self.table_exists():
            self.create_table()

    def new(self, trello_id, omnifocus_id):
        print "adding", trello_id, omnifocus_id
        try:
            created = self.create(trello_id=trello_id, omnifocus_id=omnifocus_id)
            created.save()
        except Exception:
            print "updating", trello_id
            created = self.update(omnifocus_id=omnifocus_id).where(OmnifocusTrello.trello_id == trello_id)
            created.execute()
        return created

    def by_trello_id(self, trello_id):
        try:
            item = self.get(OmnifocusTrello.trello_id == trello_id)
        except Exception:
            item = None
        finally:
            return item


class DateTimeField(_BaseFormattedField):
    db_field = 'timestamp'

    def python_value(self, value):
        if value and isinstance(value, float):
            start_time = datetime.datetime.strptime("01-01-2001", "%m-%d-%Y")
            return start_time + datetime.timedelta(seconds=value)
        return value

    year = property(_date_part('year'))
    month = property(_date_part('month'))
    day = property(_date_part('day'))
    hour = property(_date_part('hour'))
    minute = property(_date_part('minute'))
    second = property(_date_part('second'))


class BaseModel(Model):
    class Meta:
        database = database


class Attachment(BaseModel):
    containingtransactionhint = TextField(db_column='containingTransactionHint', null=True)
    context = TextField(index=True, null=True)
    creationordinal = IntegerField(db_column='creationOrdinal', null=True)
    dateadded = DateTimeField(db_column='dateAdded')  # timestamp
    datemodified = DateTimeField(db_column='dateModified')  # timestamp
    folder = TextField(index=True, null=True)
    name = TextField(null=True)
    persistentidentifier = TextField(db_column='persistentIdentifier', primary_key=True)
    perspective = TextField(index=True, null=True)
    previewpngdata = BlobField(db_column='previewPNGData', null=True)
    task = TextField(index=True, null=True)

    class Meta:
        db_table = 'Attachment'


class Context(BaseModel):
    active = IntegerField()
    allowsnextaction = IntegerField(db_column='allowsNextAction')
    altitude = FloatField(null=True)
    availabletaskcount = IntegerField(db_column='availableTaskCount')
    childrencount = IntegerField(db_column='childrenCount')
    childrenstate = IntegerField(db_column='childrenState')
    containedtaskcount = IntegerField(db_column='containedTaskCount')
    creationordinal = IntegerField(db_column='creationOrdinal', null=True)
    dateadded = DateTimeField(db_column='dateAdded')  # timestamp
    datemodified = DateTimeField(db_column='dateModified')  # timestamp
    effectiveactive = IntegerField(db_column='effectiveActive')
    latitude = FloatField(null=True)
    localnumberofduesoontasks = IntegerField(db_column='localNumberOfDueSoonTasks')
    localnumberofoverduetasks = IntegerField(db_column='localNumberOfOverdueTasks')
    locationname = TextField(db_column='locationName', null=True)
    longitude = FloatField(null=True)
    name = TextField(null=True)
    nexttaskcount = IntegerField(db_column='nextTaskCount')
    notexmldata = BlobField(db_column='noteXMLData', null=True)
    notificationflags = IntegerField(db_column='notificationFlags', null=True)
    parent = TextField(index=True, null=True)
    persistentidentifier = TextField(db_column='persistentIdentifier', primary_key=True)
    plaintextnote = TextField(db_column='plainTextNote', null=True)
    radius = FloatField(null=True)
    rank = IntegerField()
    remainingtaskcount = IntegerField(db_column='remainingTaskCount')
    totalnumberofduesoontasks = IntegerField(db_column='totalNumberOfDueSoonTasks')
    totalnumberofoverduetasks = IntegerField(db_column='totalNumberOfOverdueTasks')

    class Meta:
        db_table = 'Context'


class Folder(BaseModel):
    active = IntegerField()
    childrencount = IntegerField(db_column='childrenCount')
    childrenstate = IntegerField(db_column='childrenState')
    creationordinal = IntegerField(db_column='creationOrdinal', null=True)
    dateadded = DateTimeField(db_column='dateAdded')  # timestamp
    datemodified = DateTimeField(db_column='dateModified')  # timestamp
    effectiveactive = IntegerField(db_column='effectiveActive')
    name = TextField(null=True)
    notexmldata = BlobField(db_column='noteXMLData', null=True)
    numberofavailabletasks = IntegerField(db_column='numberOfAvailableTasks')
    numberofcontainedtasks = IntegerField(db_column='numberOfContainedTasks')
    numberofduesoontasks = IntegerField(db_column='numberOfDueSoonTasks')
    numberofoverduetasks = IntegerField(db_column='numberOfOverdueTasks')
    numberofremainingtasks = IntegerField(db_column='numberOfRemainingTasks')
    parent = TextField(index=True, null=True)
    persistentidentifier = TextField(db_column='persistentIdentifier', primary_key=True)
    plaintextnote = TextField(db_column='plainTextNote', null=True)
    rank = IntegerField()

    class Meta:
        db_table = 'Folder'


class Odometadata(BaseModel):
    key = CharField(primary_key=True)  # VARCHAR
    value = BlobField()

    class Meta:
        db_table = 'ODOMetadata'


class Perspective(BaseModel):
    creationordinal = IntegerField(db_column='creationOrdinal', null=True)
    dateadded = DateTimeField(db_column='dateAdded')  # timestamp
    datemodified = DateTimeField(db_column='dateModified')  # timestamp
    persistentidentifier = TextField(db_column='persistentIdentifier', primary_key=True)
    valuedata = BlobField(db_column='valueData', null=True)

    class Meta:
        db_table = 'Perspective'


class Projectinfo(BaseModel):
    containssingletonactions = IntegerField(db_column='containsSingletonActions')
    folder = TextField(index=True, null=True)
    foldereffectiveactive = IntegerField(db_column='folderEffectiveActive')
    lastreviewdate = DateTimeField(db_column='lastReviewDate', null=True)  # timestamp
    minimumduedate = DateTimeField(db_column='minimumDueDate', null=True)  # timestamp
    nextreviewdate = DateTimeField(db_column='nextReviewDate', null=True)  # timestamp
    nexttask = TextField(db_column='nextTask', index=True, null=True)
    numberofavailabletasks = IntegerField(db_column='numberOfAvailableTasks')
    numberofcontainedtasks = IntegerField(db_column='numberOfContainedTasks')
    numberofduesoontasks = IntegerField(db_column='numberOfDueSoonTasks')
    numberofoverduetasks = IntegerField(db_column='numberOfOverdueTasks')
    numberofremainingtasks = IntegerField(db_column='numberOfRemainingTasks')
    pk = TextField(primary_key=True)
    reviewrepetitionstring = TextField(db_column='reviewRepetitionString', null=True)
    status = TextField()
    task = TextField(index=True, null=True)
    taskblocked = IntegerField(db_column='taskBlocked')
    taskblockedbyfuturestartdate = IntegerField(db_column='taskBlockedByFutureStartDate')
    taskdatetostart = DateTimeField(db_column='taskDateToStart', null=True)  # timestamp

    class Meta:
        db_table = 'ProjectInfo'

    def get_all_project_names(self):
        to_ret = []
        projects = self.select()
        for project in projects:
            project_task = Task.get(Task.persistentidentifier == project.task)
            to_ret.append(project_task.name)
        return to_ret

    @staticmethod
    def get_trello_projects():
        to_ret = []
        folder = Folder.get(Folder.name == 'Trello')
        projects = Projectinfo.select().where(Projectinfo.folder == folder.persistentidentifier)
        for project in projects:
            project_task = Task.get(Task.persistentidentifier == project.task)
            to_ret.append(project_task.name)
        return to_ret


class Setting(BaseModel):
    creationordinal = IntegerField(db_column='creationOrdinal', null=True)
    dateadded = DateTimeField(db_column='dateAdded')  # timestamp
    datemodified = DateTimeField(db_column='dateModified')  # timestamp
    persistentidentifier = TextField(db_column='persistentIdentifier', primary_key=True)
    valuedata = BlobField(db_column='valueData', null=True)

    class Meta:
        db_table = 'Setting'


class Task(BaseModel):
    blocked = IntegerField()
    blockedbyfuturestartdate = IntegerField(db_column='blockedByFutureStartDate')
    childrencount = IntegerField(db_column='childrenCount')
    childrencountavailable = IntegerField(db_column='childrenCountAvailable')
    childrencountcompleted = IntegerField(db_column='childrenCountCompleted')
    childrenstate = IntegerField(db_column='childrenState')
    completewhenchildrencomplete = IntegerField(db_column='completeWhenChildrenComplete')
    containingprojectcontainssingletons = IntegerField(db_column='containingProjectContainsSingletons')
    containingprojectinfo = TextField(db_column='containingProjectInfo', index=True, null=True)
    containsnexttask = IntegerField(db_column='containsNextTask')
    context = TextField(index=True, null=True)
    creationordinal = IntegerField(db_column='creationOrdinal', null=True)
    dateadded = DateTimeField(db_column='dateAdded')  # timestamp
    datecompleted = DateTimeField(db_column='dateCompleted', null=True)  # timestamp
    datedue = DateTimeField(db_column='dateDue', null=True)  # timestamp
    datemodified = DateTimeField(db_column='dateModified')  # timestamp
    datetostart = DateTimeField(db_column='dateToStart', null=True)  # timestamp
    effectivecontainingprojectinfoactive = IntegerField(db_column='effectiveContainingProjectInfoActive')
    effectivecontainingprojectinforemaining = IntegerField(db_column='effectiveContainingProjectInfoRemaining')
    effectivedatedue = DateTimeField(db_column='effectiveDateDue', null=True)  # timestamp
    effectivedatetostart = DateTimeField(db_column='effectiveDateToStart', null=True)  # timestamp
    effectiveflagged = IntegerField(db_column='effectiveFlagged')
    effectiveininbox = IntegerField(db_column='effectiveInInbox')
    estimatedminutes = IntegerField(db_column='estimatedMinutes', null=True)
    flagged = IntegerField()
    hascompleteddescendant = IntegerField(db_column='hasCompletedDescendant')
    hasflaggedtaskintree = IntegerField(db_column='hasFlaggedTaskInTree')
    hasunestimatedleaftaskintree = IntegerField(db_column='hasUnestimatedLeafTaskInTree')
    ininbox = IntegerField(db_column='inInbox')
    isduesoon = IntegerField(db_column='isDueSoon')
    isoverdue = IntegerField(db_column='isOverdue')
    maximumestimateintree = IntegerField(db_column='maximumEstimateInTree', null=True)
    minimumestimateintree = IntegerField(db_column='minimumEstimateInTree', null=True)
    name = TextField(null=True)
    nexttaskofprojectinfo = TextField(db_column='nextTaskOfProjectInfo', index=True, null=True)
    notexmldata = BlobField(db_column='noteXMLData', null=True)
    parent = TextField(index=True, null=True)
    persistentidentifier = TextField(db_column='persistentIdentifier', primary_key=True)
    plaintextnote = TextField(db_column='plainTextNote', null=True)
    projectinfo = TextField(db_column='projectInfo', index=True, null=True)
    rank = IntegerField()
    repetitionmethodstring = TextField(db_column='repetitionMethodString', null=True)
    repetitionrulestring = TextField(db_column='repetitionRuleString', null=True)
    sequential = IntegerField()

    class Meta:
        db_table = 'Task'

    def by_id(self, id):
        try:
            item = self.get(Task.persistentidentifier == id)
        except Exception:
            item = None
        finally:
            return item


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

    Projectinfo = Projectinfo
    Task = Task

    @classmethod
    def make_project(cls, project_name):
        properties = dict(name=project_name)
        cls._communicate(cls.PROJECT_TEMPLATE, properties)

    @classmethod
    def add_task(cls, project_name, name, *args, **kwargs):
        properties = dict(name=name)
        for key, value in kwargs.iteritems():
            properties[key] = value
        resp = cls._communicate(cls.TASK_TEMPLATE, properties, project_name=project_name)
        task_id = cls._parse_response(resp)
        return task_id

    @classmethod
    def _format_property_string(cls, d):
        key_values = ", ".join(['%s: "%s"' % item for item in d.iteritems()])
        return "{%s}" % key_values

    @classmethod
    def _communicate(cls, template, properties, *args, **kwargs):
        p = Popen(["osascript", "-"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        return p.communicate(template.format(properties=cls._format_property_string(properties), **kwargs))

    @staticmethod
    def _parse_response(response, resp_type='task'):
        if resp_type == 'task':
            search = re.search(r"task id (\S+) of document id (\w+)", response[0])
            if search:
                return search.group(1)
