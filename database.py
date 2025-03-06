import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

# Conectar ao banco de dados
conn = sqlite3.connect("emprestimos.db")
c = conn.cursor()

# Criar tabela se não existir
c.execute('''
CREATE TABLE IF NOT EXISTS emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    valor REAL NOT NULL,
    juros REAL NOT NULL,
    data_emprestimo TEXT NOT NULL,
    proximo_pagamento TEXT NOT NULL,
    periodo_juros INTEGER NOT NULL
)
''')
conn.commit()

# Funções do sistema
def calcular_valor_pagar(valor, juros):
    return valor * (1 + juros / 100)

def adicionar_emprestimo():
    nome = entry_nome.get()
    valor = float(entry_valor.get())
    juros = float(entry_juros.get())
    periodo = int(entry_periodo.get())
    
    if not nome or valor <= 0 or juros < 0 or periodo <= 0:
        messagebox.showerror("Erro", "Preencha todos os campos corretamente!")
        return
    
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    proximo_pagamento = (datetime.now() + timedelta(days=periodo)).strftime("%Y-%m-%d")
    c.execute("INSERT INTO emprestimos (nome, valor, juros, data_emprestimo, proximo_pagamento, periodo_juros) VALUES (?, ?, ?, ?, ?, ?)",
              (nome, valor, juros, data_hoje, proximo_pagamento, periodo))
    conn.commit()
    atualizar_tabela()
    entry_nome.delete(0, tk.END)
    entry_valor.delete(0, tk.END)
    entry_juros.delete(0, tk.END)
    entry_periodo.delete(0, tk.END)
    messagebox.showinfo("Sucesso", "Empréstimo cadastrado com sucesso!")

def listar_emprestimos():
    c.execute("SELECT * FROM emprestimos")
    return c.fetchall()

def atualizar_tabela():
    for row in tree.get_children():
        tree.delete(row)
    
    hoje = datetime.now().date()
    
    for emp in listar_emprestimos():
        valor_pagar = calcular_valor_pagar(emp[2], emp[3])
        data_pagamento = datetime.strptime(emp[5], "%Y-%m-%d").date()
        
        linha = list(emp)
        linha.append(f"R$ {valor_pagar:.2f}")
        
        if data_pagamento < hoje:
            tree.insert("", "end", values=linha, tags=('atrasado',))
        else:
            tree.insert("", "end", values=linha)

def excluir_emprestimo():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Aviso", "Selecione um empréstimo para excluir!")
        return
    
    resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este empréstimo?")
    if resposta:
        emprestimo_id = tree.item(selected_item)['values'][0]
        c.execute("DELETE FROM emprestimos WHERE id=?", (emprestimo_id,))
        conn.commit()
        atualizar_tabela()
        messagebox.showinfo("Sucesso", "Empréstimo excluído com sucesso!")

def editar_emprestimo():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Aviso", "Selecione um empréstimo para editar!")
        return
    
    emprestimo_id = tree.item(selected_item)['values'][0]
    c.execute("SELECT * FROM emprestimos WHERE id=?", (emprestimo_id,))
    dados = c.fetchone()
    
    edit_window = tk.Toplevel(root)
    edit_window.title("Editar Empréstimo")
    
    tk.Label(edit_window, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    nome_entry = tk.Entry(edit_window)
    nome_entry.grid(row=0, column=1)
    nome_entry.insert(0, dados[1])
    
    tk.Label(edit_window, text="Valor R$:").grid(row=1, column=0, padx=5, pady=5)
    valor_entry = tk.Entry(edit_window)
    valor_entry.grid(row=1, column=1)
    valor_entry.insert(0, dados[2])
    
    tk.Label(edit_window, text="Juros %:").grid(row=2, column=0, padx=5, pady=5)
    juros_entry = tk.Entry(edit_window)
    juros_entry.grid(row=2, column=1)
    juros_entry.insert(0, dados[3])
    
    tk.Label(edit_window, text="Período (dias):").grid(row=3, column=0, padx=5, pady=5)
    periodo_entry = tk.Entry(edit_window)
    periodo_entry.grid(row=3, column=1)
    periodo_entry.insert(0, dados[6])
    
    def salvar_edicao():
        novo_nome = nome_entry.get()
        novo_valor = float(valor_entry.get())
        novo_juros = float(juros_entry.get())
        novo_periodo = int(periodo_entry.get())
        
        if not novo_nome or novo_valor <= 0 or novo_juros < 0 or novo_periodo <= 0:
            messagebox.showerror("Erro", "Preencha todos os campos corretamente!")
            return
        
        c.execute('''
            UPDATE emprestimos SET
                nome = ?,
                valor = ?,
                juros = ?,
                periodo_juros = ?
            WHERE id = ?
        ''', (novo_nome, novo_valor, novo_juros, novo_periodo, emprestimo_id))
        conn.commit()
        atualizar_tabela()
        edit_window.destroy()
        messagebox.showinfo("Sucesso", "Empréstimo atualizado com sucesso!")
    
    tk.Button(edit_window, text="Salvar", command=salvar_edicao).grid(row=4, columnspan=2, pady=10)

def exportar_clientes():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    
    if not file_path:
        return
    
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Nome", "Valor", "Juros", "Data Empréstimo", "Próx. Pagamento", "Período", "Valor a Pagar"])
        
        c.execute("SELECT * FROM emprestimos")
        for emp in c.fetchall():
            valor_pagar = calcular_valor_pagar(emp[2], emp[3])
            linha = list(emp)
            linha.append(f"R$ {valor_pagar:.2f}")
            writer.writerow(linha)
    
    messagebox.showinfo("Sucesso", f"Dados exportados para:\n{file_path}")

# Interface Gráfica
root = tk.Tk()
root.title("Gerenciador de Empréstimos")
root.geometry("1000x600")

# Configurar estilo
style = ttk.Style()
style.configure("Treeview", rowheight=25, font=('Arial', 10))
style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
style.map('Treeview', background=[('selected', '#347083')])

# Formulário principal
frame_form = tk.Frame(root)
frame_form.pack(pady=10)

tk.Label(frame_form, text="Nome:").grid(row=0, column=0, padx=5)
entry_nome = tk.Entry(frame_form, width=25)
entry_nome.grid(row=0, column=1, padx=5)

tk.Label(frame_form, text="Valor R$:").grid(row=0, column=2, padx=5)
entry_valor = tk.Entry(frame_form, width=15)
entry_valor.grid(row=0, column=3, padx=5)

tk.Label(frame_form, text="Juros %:").grid(row=1, column=0, padx=5)
entry_juros = tk.Entry(frame_form, width=10)
entry_juros.grid(row=1, column=1, padx=5)

tk.Label(frame_form, text="Período (dias):").grid(row=1, column=2, padx=5)
entry_periodo = tk.Entry(frame_form, width=10)
entry_periodo.grid(row=1, column=3, padx=5)

btn_adicionar = tk.Button(frame_form, text="Adicionar Empréstimo", command=adicionar_emprestimo)
btn_adicionar.grid(row=2, column=0, columnspan=4, pady=10)

# Botões de controle
frame_controles = tk.Frame(root)
frame_controles.pack(pady=10)

btn_editar = tk.Button(frame_controles, text="✏️ Editar", command=editar_emprestimo, width=12)
btn_editar.pack(side=tk.LEFT, padx=5)

btn_excluir = tk.Button(frame_controles, text="🗑️ Excluir", command=excluir_emprestimo, width=12)
btn_excluir.pack(side=tk.LEFT, padx=5)

btn_exportar = tk.Button(frame_controles, text="📤 Exportar", command=exportar_clientes, width=12)
btn_exportar.pack(side=tk.LEFT, padx=5)

# Tabela de empréstimos
columns = ("ID", "Nome", "Valor", "Juros", "Data Empréstimo", "Próx. Pagamento", "Período", "Valor a Pagar")
tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")

# Configurar tags
tree.tag_configure('atrasado', background='#ff9999')

# Configurar colunas
widths = [50, 180, 100, 80, 120, 120, 80, 120]
headers = ["ID", "Nome", "Valor (R$)", "Juros (%)", "Data Empréstimo", "Próx. Pagamento", "Período (dias)", "Valor a Pagar"]

for col, width, header in zip(columns, widths, headers):
    tree.heading(col, text=header)
    tree.column(col, width=width, anchor=tk.CENTER)

tree.pack(expand=True, fill="both", padx=10, pady=5)

atualizar_tabela()

root.mainloop()
conn.close()