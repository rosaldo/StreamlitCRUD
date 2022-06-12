#!/usr/bin/env python3
# coding: utf-8

# to run this file:
# streamlit run crud_clientes.py --server.port 8501

import os

import streamlit as st
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from streamlit_autorefresh import st_autorefresh

Base = declarative_base()


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cnpj = Column(String)
    email = Column(String)
    active = Column(Boolean)


class DBase:
    version = "1.0.0"

    def __init__(self):
        script_name = os.path.basename(__file__)[:-3]
        script_path = os.path.dirname(os.path.realpath(__file__))
        db_name = f"sqlite:///{script_path}{os.sep}{script_name}.sqlite3"
        self.engine = create_engine(
            db_name,
            poolclass=StaticPool,
        )
        self.session = sessionmaker(bind=self.engine)
        if not self.engine.has_table("client"):
            Client.__table__.create(self.engine)
        session = self.session()
        old_client = session.query(Client).filter_by(id=999999).first()
        if not old_client:
            new_client = Client(
                id=999999,
                name="The Best Client",
                cnpj="12345678000123",
                email="thebestclient@mail.com",
                active=1,
            )
            session.add(new_client)
        session.commit()
        session.close()

    def execute_sql(self, sql):
        conn = self.engine.connect()
        trans = conn.begin()
        try:
            result = conn.execute(sql)
            trans.commit()
            conn.close()
            return result
        except Exception:
            trans.rollback()

    def get_client(self, id=None):
        sql = """
            select id, name, cnpj, email, active
            from client
            """
        if id:
            sql += f"where id = {id}"
        data = self.execute_sql(sql)
        if data:
            client = []
            for rec in data:
                client.append(
                    {
                        "id": rec.id,
                        "name": rec.name,
                        "cnpj": rec.cnpj,
                        "email": rec.email,
                        "active": rec.active,
                    }
                )
            return client
        else:
            return {}

    def update_client(self, id, name, cnpj, email, active):
        sql = f"""
            update client
            set name="{name}", cnpj="{cnpj}", email="{email}", active="{active}" 
            where id="{id}"
            """
        self.execute_sql(sql)

    def add_client(self, name, cnpj, email, active):
        sql = f"""
            insert into
            client (name, cnpj, email, active)
            values ("{name}", "{cnpj}", "{email}", "{active}")
            """
        self.execute_sql(sql)

    def delete_client(self, id):
        sql = f"""
            delete
            from client
            where id="{id}"
            """
        self.execute_sql(sql)


class Crud:
    version = "1.0.0"
    db = DBase()
    action = st.experimental_get_query_params()

    def __init__(self):
        st.set_page_config(
            page_title="CRUD Client",
            layout="wide",
        )
        bootstrap = """
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css"
            rel="stylesheet"
            integrity="sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor"
            crossorigin="anonymous">
            """
        st.markdown(bootstrap, unsafe_allow_html=True)
        hide_menu_footer = """
            <style>
                #MainMenu, footer {
                    visibility: hidden;
                }
            </style>
            """
        st.markdown(hide_menu_footer, unsafe_allow_html=True)
        self.header()
        if not self.action:
            self.list()
        if self.action.get("new"):
            self.new()
        if self.action.get("ed"):
            self.edit(self.action.get("ed")[0])
        if self.action.get("rm"):
            self.remove(self.action.get("rm")[0])

    def header(self):
        with st.container():
            html_style = """
                <style>
                    span {
                        font-style: italic;
                        font-weight: bold;
                        font-size: 30pt;
                    }
                </style>
                """
            st.markdown(html_style, unsafe_allow_html=True)
            col1, col2 = st.columns((10, 1))
            col1.header("CRUD Client")
            if not self.action:
                html_button = "<a href='?new=true' target='_self'><button class='btn btn-outline-primary'>New Client</button></a>"
                col2.markdown(html_button, unsafe_allow_html=True)

    def list(self):
        with st.container():
            client = self.db.get_client()
            if client:
                html_table = """
                    <link href="https://fonts.googleapis.com/css?family=Roboto:300,300i,500" rel="stylesheet"/>
                    <style>
                        table {
                            width: 100%;
                            border-collapse: collapse;
                        }

                        tr:nth-of-type(odd) {
                            background: #f4f4f4;
                        }

                        tr:nth-of-type(even) {
                            background: #fff;
                        }

                        tr.head {
                            background: #888;
                            color: #fff;
                            font-weight: 600;
                            font-size: 17pt;
                            text-align: center;
                        }

                        td {
                            text-align: left;
                        }

                        td,
                        th {
                            padding: 10px;
                            border: 1px solid #ccc;
                        }

                        td:nth-of-type(1) {
                            font-weight: 500 !important;
                        }

                        td {
                            font-family: 'Roboto', sans-serif !important;
                            font-weight: 300;
                            line-height: 20px;
                            vertical-align: middle;
                        }

                        td.center{
                            text-align: center;
                        }

                        @media only screen and (max-width: 760px),
                        (min-device-width: 768px) and (max-device-width: 1024px) {
                            table.responsive,
                            .responsive thead,
                            .responsive tbody,
                            .responsive th,
                            .responsive td,
                            
                            .responsive tr {
                                display: block !important;
                            }

                            .responsive thead tr {
                                position: absolute !important;
                                top: -9999px;
                                left: -9999px;
                            }

                            .responsive tr {
                                border: 1px solid #ccc;
                            }

                            .responsive td {
                                border: none;
                                border-bottom: 1px solid #eee !important;
                                position: relative !important;
                                padding-left: 25% !important;
                            }

                            .responsive td:before {
                                position: absolute !important;
                                top: 6px;
                                left: 6px;
                                width: 45%;
                                padding-right: 10px;
                                white-space: nowrap !important;
                                font-weight: 500 !important;
                            }
                            
                            .responsive td:before {
                                content: attr(data-table-header) !important;
                            }
                        }
                    </style>
                    <table class="dataframe table responsive">
                    <thead>
                    <tr class='head'>
                    <th>NAME</th>
                    <th>CNPJ</th>
                    <th>EMAIL</th>
                    <th>ACTIVE</th>
                    <th>ACTIONS</th>
                    </tr>
                    </thead>
                    <tbody>
                    """
                for row in client:
                    html_table += "<tr>"
                    html_table += "<td>" + str(row.get("name")) + "</td>"
                    html_table += "<td>" + str(row.get("cnpj")) + "</td>"
                    html_table += "<td>" + str(row.get("email")) + "</td>"
                    html_table += (
                        "<td class='center'>"
                        + ("Yes" if row.get("active") == 1 else "No")
                        + "</td>"
                    )
                    html_table += (
                        "<td class='center'><a href='?ed="
                        + str(row.get("id"))
                        + "' target='_self'><button class='btn btn-outline-warning btn-sm'>EDIT</button></a> <a href='?rm="
                        + str(row.get("id"))
                        + "' target='_self'><button class='btn btn-outline-danger btn-sm'>REMOVE</button></a></td>"
                    )
                    html_table += "</tr>"
                html_table += "</tbody></table>"
                st.markdown(html_table, unsafe_allow_html=True)

    def remove(self, id):
        self.db.delete_client(id)
        st.experimental_set_query_params()
        st_autorefresh(interval=1, limit=2)

    def new(self):
        with st.container():
            with st.form("add_client"):

                col1, col2 = st.columns((1, 5))
                active = col1.number_input("Active", min_value=0, max_value=1)
                name = col2.text_input("Name").upper()

                col1, col2 = st.columns((2, 4))
                cnpj = col1.text_input("CNPJ")
                email = col2.text_input("Email")

                col1, col2, col3, col4 = st.columns((6, 1, 1, 6))
                col1.empty()
                go_back = col2.form_submit_button("Back")
                add_client = col3.form_submit_button("Add")
                col4.empty()

            if add_client and name != "" and cnpj != "":
                self.db.add_client(name, cnpj, email, active)
                st.experimental_set_query_params()
                st_autorefresh(interval=1, limit=2)

            if go_back:
                st.experimental_set_query_params()
                st_autorefresh(interval=1, limit=2)

    def edit(self, id):
        with st.container():
            client = self.db.get_client(id)[0]
            with st.form("update_client"):

                col1, col2 = st.columns((1, 5))
                active = col1.number_input(
                    "Active", value=client.get("active"), min_value=0, max_value=1
                )
                name = col2.text_input("Name", value=client.get("name"))

                col1, col2 = st.columns((2, 4))
                cnpj = col1.text_input("CNPJ", value=client.get("cnpj"))
                email = col2.text_input("Email", value=client.get("email"))

                col1, col2, col3, col4 = st.columns((6, 1, 1, 6))
                col1.empty()
                go_back = col2.form_submit_button("Back")
                update_client = col3.form_submit_button("Update")
                col4.empty()

            if update_client and name != "" and cnpj != "":
                self.db.update_client(id, name, cnpj, email, active)
                st.experimental_set_query_params()
                st_autorefresh(interval=1, limit=2)

            if go_back:
                st.experimental_set_query_params()
                st_autorefresh(interval=1, limit=2)


Crud()
