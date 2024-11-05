
from fasthtml.common import *
import sqlite3
import os
from pathlib import Path
import pandas as pd

app, rt = fast_app(    
    hdrs=(
        Link(rel='stylesheet', href='test.css', type='text/css'),
        ))

DB_DIR = Path("databases")

def get_db_files():
    return [f.name for f in DB_DIR.glob("*.db")]

def get_tables(db_name):
    conn = sqlite3.connect(DB_DIR / db_name)
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_data(db_name, table_name):
    global table
    print(table)

    if db_name is None:
        print('Erro no DB')
        raise ValueError("Nome do banco de dados não fornecido")
    if table_name is None:
        print('Erro no table')
        table_name = table
        raise ValueError("Nome da tabela não fornecido")
    
    conn = sqlite3.connect(DB_DIR / db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM '{table_name}'")
    columns = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
    
    conn.close()
    return columns, data, df

def math_df(df_math):
    df_math['Media'] = df_math.filter(like='P', axis=1).mean(axis=1).round(2)
    df_math['Total'] = df_math.filter(like='P', axis=1).sum(axis=1)
    return df_math




@rt('/')
def home():
    db_files = get_db_files()
    return Div(
        Form(
            Select(
                Option("Select a database...", value=""),
                *[Option(db, value=db) for db in db_files],
                name="database",
                onchange="this.form.action='/selecionar-banco'; this.form.submit()",
            ),
            action="/show-data",
            method="get"
        ),
        id="tables-container"
    )           
    
@rt('/selecionar-banco')
def selecionar_banco(request):
    database = request.query_params.get("database")
    tabelas = get_tables(database)
    ultima_tabela = tabelas[-1]
    return RedirectResponse(url=f"/show-data?database={database}&table={ultima_tabela}")    

database = ''
table = ''

@rt('/show-data')
def show_data(request):
    global database, table
    print(request.query_params.get("database"))
    database = request.query_params.get("database")
    table = request.query_params.get("table")
    
    
    if database is None:
        return Div("Banco de dados selecionada")
    # if table is None:
    #     table = get_tables(database)[-1]
        # return Div("Tabela não selecionada")    
    
    columns, data, df = get_table_data(database, table)
    
    df = math_df(df)

    table_layout = Table(
        Thead(*[Th(col) for col in df.columns]),
        Tbody(
            *[Tr(*[Td(cell) for cell in row]) for row in df.values],
            style={"padding": "0", "font-size": "13px"}
        ),
        style={"border-collapse": "collapse", "width": "100%"},
        cls="tabela-fixada",
        id="tabela"
    )
    
    db_select = Select(
        Option(database, value=database),
        *[Option(db, value=db) for db in get_db_files() if db != database],
        name="database",
        onchange="this.form.action='/selecionar-banco'; this.form.submit()",
        style={"margin": "5px"}
    )
    button_select = Div(
        *[Button(t, 
                ontouchstart=f"window.location.href='/show-data?database={database}&table={t}'",
                # onclick=f"window.location.href='/show-data?database={database}&table={t}'",
                onmousedown=f"window.location.href='/show-data?database={database}&table={t}'",
                style={"padding": "5px", "font-size": "12px", "margin": "5px"}
                ) 
        for t in get_tables(database)]
    )
       
    # table_select = Select(
    #     Option(table, value=table),
    #     *[Option(t, value=t) for t in get_tables(database) if t != table],
    #     name="table",
    #     onchange=f"window.location.href='/show-data?database={database}&table=' + this.value"
    # )
    
    

    return Div(
        Form(
            db_select,
            # table_select,
            button_select,
        ),
        table_layout
    )

serve()