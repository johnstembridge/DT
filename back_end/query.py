from flask import render_template, redirect, url_for, request

from front_end.form_helpers import flash_errors, render_link, url_pickle_dump, url_pickle_load, extract_fields_map
from front_end.query_form import QueryForm
from front_end.extract_form import ExtractForm
from back_end.interface import get_attr, get_members_for_query


class Query:

    @staticmethod
    def select(title):
        form = QueryForm()
        form.set_status_choices()
        if form.submit.data:
            form.display_fields.data = [int(v) for v in form.display_fields.data]
            if form.validate_on_submit():
                query_clauses = form.find_members()
                display_fields = [c[1] for c in form.display_fields.choices if c[0] in form.display_fields.data]
                return redirect(url_for(
                    'extracts_show',
                    page=1,
                    query_clauses=url_pickle_dump(query_clauses),
                    display_fields=url_pickle_dump(display_fields))
                )
            elif form.errors:
                flash_errors(form)

        return render_template('query.html', form=form, render_link=render_link, title=title)

    @staticmethod
    def extract_found():
        pass  # ToDo

    @staticmethod
    def show_found():
        page = request.args.get('page', 1, int)
        query_clauses = url_pickle_load(request.args.get('query_clauses'))
        display_fields = url_pickle_load(request.args.get('display_fields'))
        form = ExtractForm()
        query = get_members_for_query(query_clauses)
        page = form.populate_result(clauses=url_pickle_dump(query_clauses), fields=url_pickle_dump(display_fields),
                                    query=query, page_number=page)
        fields = {k: extract_fields_map[k] for k in display_fields}
        return render_template('extract.html', form=form, render_link=render_link, data=page.items, fields=fields,
                               get_attr=get_attr)

    @staticmethod
    def extract():
        query_clauses = url_pickle_load(request.args.get('query_clauses'))
        display_fields = url_pickle_load(request.args.get('display_fields'))
        members = get_members_for_query(query_clauses)
        csv = []
        head = display_fields
        fields = [extract_fields_map[k] for k in display_fields]
        csv.append(head)
        for member in members:
            row = [get_attr(member, field) for field in fields]
            csv.append(row)
        return csv

    @staticmethod
    def bulk_update():
        form = QueryForm()
        form.set_status_choices()
        if form.validate_on_submit():
            if form.submit.data:
                query_clauses = url_pickle_load(request.args.get('query_clauses'))
                query = get_members_for_query(query_clauses)
                updates = form.get_updates()
                # ToDo: update here
                # flash updated
                return  ##redirect(url_for('extracts_bulk_update', query_clauses=query_clauses))
        elif form.errors:
            flash_errors(form)

        return render_template('query.html', form=form, render_link=render_link, title='Bulk update')
