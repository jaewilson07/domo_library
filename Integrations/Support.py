from dataclasses import dataclass, field
from typing import List, Union
import aiohttp

from ..utils.DictDot import DictDot
from ..utils.Base import Base

import Library.Trello.TrelloAuth as ta
import Library.Trello.TrelloUtils as tu
import Library.Trello.TrelloCard as tc

from Library.Trello.get_data import get_data
import datetime as dt


@dataclass
class SupportTicket(Base):
    ticket_id: str
    subject: str
    board_id: str = None
    list_id: str = None
    card_id: str = None
    description: str = None
    create_date: dt.datetime = None
    date_closed: dt.datetime = None
    last_updated: dt.datetime = None
    status: str = None
    status_id: str = None
    category: str = None
    category_id: str = None

    labels: list = None
    other_label_ids: list = None
    owner: str = None

    @classmethod
    def _create_from_domo_obj(cls, json_obj: dict, status_labels_list=None):
        dd = DictDot(json_obj)

        dd_last_updated = getattr(dd, 'last comment date') or None

        ticket = cls(
            ticket_id=str(dd.CaseNumber_Text),
            subject=dd.Subject,
            create_date=tu.trello_timestr_to_datetime(dd.CreatedDate),
            date_closed=tu.trello_timestr_to_datetime(
                dd.ClosedDate) if dd.ClosedDate else None,
            last_updated=tu.trello_timestr_to_datetime(
                dd_last_updated) if dd_last_updated else None,
            status=dd.Status,
            category=dd.Support_Category__c,
            owner=getattr(dd, 'Contact.Email')
        )

        if status_labels_list:
            ticket.map_domo_property_to_label('status', status_labels_list)
            ticket.map_domo_property_to_label('category', status_labels_list)

        return ticket

    def map_domo_property_to_label(self, property_name, labels_list=None):
        if getattr(self, property_name):
            property_match = next((label for label in labels_list if label.name == getattr(
                self, property_name)), None)

            if property_match:
                setattr(self, f"{property_name}_id", property_match.id)

    @classmethod
    def _create_from_trellocard(cls, tcard=tc.TrelloCard, status_labels_list=None):
        ticket = cls(
            ticket_id=str(tcard.name.split(' || ')[0]),
            subject=tcard.name.split(' || ')[1],
            board_id=tcard.board_id,
            list_id=tcard.list_id,
            card_id=tcard.id,
            labels=tcard.labels,
            description=tcard.description
        )

        if status_labels_list:
            ticket.map_trellocard_labels(status_labels_list)

        return ticket

    def map_trellocard_labels(self, labels_list):
        if not self.labels:
            return

        # status_labels_ids = [label.id for label in labels_list if label.__dict__.get('is_status_label')== True]
        # category_labels_ids = [label.id for label in labels_list if label.__dict__.get('is_category_label')== True]

        for card_label in self.labels:
            label_match = next(
                (label for label in labels_list if label.id == card_label.id), None)

            if not label_match:
                return

            if label_match.__dict__.get('is_status_label'):
                self.status_id = label_match.id
                self.status = label_match.name

            elif label_match.__dict__.get('is_category_label'):
                self.category_id = label_match.id
                self.category = label_match.name

            else:
                if not self.other_label_ids:
                    self.other_label_ids = []
                self.other_label_ids.append(label_match.id)

    def generate_trello_card(self) -> tc.TrelloCard:
        t_card = tc.TrelloCard(
            id=self.card_id,
            name=f"{self.ticket_id} || {self.subject}",
            list_id=self.list_id,
            board_id=self.board_id,
            start_date=tu.trello_datetime_to_str(self.create_date),
            description=self.description
        )
        return t_card
