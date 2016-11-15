from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for, request
from flask_admin.model import typefmt
from datetime import datetime


class AdminView(ModelView):

    def __init__(self, *args, **kwargs):
        super(AdminView, self).__init__(*args, **kwargs)
        self.static_folder = 'static'

        self.column_formatters = dict(typefmt.BASE_FORMATTERS)
        self.column_formatters.update({
                type(None): typefmt.null_formatter,
                datetime: self.date_format,
            })

        self.column_type_formatters = self.column_formatters

    def date_format(self, view, value):
        return value.strftime('%B-%m-%Y %I:%M:%p')

    def is_accessible(self):
        return session.get('user') == 'Administrator'

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home', next=request.url))


class TopicView(AdminView):

    def __init__(self, *args, **kwargs):
        super(TopicView, self).__init__(*args, **kwargs)

    column_list = ('title', 'date_created', 'date_modified', 'total_vote_count', 'status')
    column_searchable_list = ('title',)
    column_default_sort = ('date_created', True)
    column_filters = ('status',)
    column_sortable_list = ('total_vote_count',)
