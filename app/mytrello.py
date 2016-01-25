from trello import TrelloClient
from omnifocus_model import OmnifocusTasks, OmnifocusTrello

client = TrelloClient()


class TrelloBoard(object):
    def __init__(self, board):
        self.trello_board = board

    def __repr__(self):
        return self.trello_board.__repr__()

    def __getattr__(self, name):
        if hasattr(self.trello_board, name):
            return getattr(self.trello_board, name)
        else:
            # Default behaviour
            raise AttributeError

    def get_member_name(self, member_id):
        member = client.get_member(member_id)
        return member.full_name.split(' ')[0]

    @property
    def lists(self):
        return self.trello_board.get_lists(None)

    @property
    def all_cards(self):
        return self.trello_board.get_cards()


class TrelloBoards(list):
    VALID_BOARDS = {
        "2016 SP1": {"done_list": "Shit that is DONE!"}
    }

    COMPLETED_BOARDS = [value.get('done_list') for key, value in VALID_BOARDS.iteritems()]

    def __init__(self):
        self.omnifocus = OmnifocusTasks()
        self._boards_fetched = False

    @classmethod
    def init(cls):
        self = cls()
        return self.boards

    @property
    def cards_for_all_boards(self):
        to_ret = []
        for board in self.boards:
            to_ret.extend(board.all_cards)
        return to_ret

    @property
    def boards(self):
        if not self._boards_fetched:
            self.extend(map(TrelloBoard, self._get_boards()))
            self._boards_fetched = True
        return self

    def list_id_by_name(self, board, name):
        for list_ in board.get_lists(None):
            if list_.name == name:
                return list_.id
        return None

    def _get_boards(self, valid_only=True):
        boards = client.list_boards()
        if valid_only:
            return [board for board in boards
                    if board.name in self.VALID_BOARDS.keys() and
                    board.name not in self.COMPLETED_BOARDS]
        return boards

    def run(self):
        self._check_projects_names()
        self._check_for_tasks()
        self._check_omnifocus_completed()

    def _check_projects_names(self):
        omnifocus_projects = self.omnifocus.Projectinfo.get_trello_projects()
        for board in self.boards:
            for list_ in board.lists:
                project_name = "%s - %s" % (board.name, list_.name)
                if project_name not in omnifocus_projects:
                    self.omnifocus.make_project(project_name)

    def _check_for_tasks(self):
        for board in self.boards:
            for list_ in board.lists:
                for card in list_.list_cards():
                    project_name = "%s - %s" % (board.name, list_.name)
                    trello_of = OmnifocusTrello().by_trello_id(card.id)
                    if (trello_of and not self.omnifocus.Task().by_id(trello_of.omnifocus_id) or
                            not trello_of):
                        print "making task", card.name
                        of_task_id = self.omnifocus.add_task(project_name, card.name)
                        OmnifocusTrello().new(card.id, of_task_id)
                    else:
                        continue
                        # print card.name, "already exists"

    def _check_for_moved_task(self, card):




    def _check_omnifocus_completed(self):
        for card in self.cards_for_all_boards:
            if card.board.name in self.COMPLETED_BOARDS:
                print "already in done. moving on..."
                continue
            trello_of = OmnifocusTrello().by_trello_id(card.id)
            omnifocus_task = self.omnifocus.Task().by_id(trello_of.omnifocus_id)
            if omnifocus_task and omnifocus_task.datecompleted:
                print "TASK COMPLETE. MOVING TO DONE"
                done_list_id = self.list_id_by_name(card.board,
                                                    self.VALID_BOARDS[card.board.name]['done_list'])
                card.change_list(done_list_id)


"""
    - if card not in omnifocus at all, create it
    - if the card has move activity and the new location is not the same as the OF project, move it
    - if card's date_modified newer than OF's task, update the task
    - if OF task is complete, move it to the done list

"""








def make_projects():
    for board in client.list_boards():
        if board.name in VALID_BOARDS:
            for the_list in board.get_lists(None):
                project_name = "%s - %s" % (board.name, the_list.name)
                Omnifocus.make_project(project_name)
                for card in the_list.list_cards():
                    names = []
                    if card.member_ids:
                        for member_id in card.member_ids:
                            names.append("(%s)" % get_member_name(member_id))

                    Omnifocus.add_task(project_name, "%s %s" % (" ".join(names), card.name))



    for board in client.list_boards():
        if board.name in VALID_BOARDS:
            for the_list in board.get_lists(None):
                project_name = "%s - %s" % (board.name, the_list.name)
                for card in the_list.list_cards():
                    try:
                        print card.date_list_activity
                    except Exception:
                        print "didn't work for", card.name
