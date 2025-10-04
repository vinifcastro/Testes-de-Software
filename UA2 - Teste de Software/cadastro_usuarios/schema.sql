PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  senha_hash TEXT NOT NULL,
  cpf TEXT NOT NULL UNIQUE,
  data_nascimento TEXT NOT NULL,
  telefone TEXT,
  cep TEXT NOT NULL,
  renda_mensal REAL NOT NULL,
  aceite_termos INTEGER NOT NULL CHECK (aceite_termos IN (0,1)),
  created_at TEXT NOT NULL
);
