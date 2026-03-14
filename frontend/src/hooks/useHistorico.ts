import { useState, useCallback } from 'react';

interface ItemHistorico {
  expressao: string;
  latex_resultado: string;
  timestamp: number;
}

const STORAGE_KEY = 'algebrow_historico';
const MAX_ITENS = 50;

function carregarDoStorage(): ItemHistorico[] {
  try {
    const dados = localStorage.getItem(STORAGE_KEY);
    return dados ? JSON.parse(dados) : [];
  } catch {
    return [];
  }
}

function salvarNoStorage(itens: ItemHistorico[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(itens.slice(0, MAX_ITENS)));
}

export function useHistorico() {
  const [itens, setItens] = useState<ItemHistorico[]>(carregarDoStorage);

  const adicionar = useCallback((expressao: string, latex_resultado: string) => {
    setItens(prev => {
      const novo = [{ expressao, latex_resultado, timestamp: Date.now() }, ...prev];
      const limitado = novo.slice(0, MAX_ITENS);
      salvarNoStorage(limitado);
      return limitado;
    });
  }, []);

  const limpar = useCallback(() => {
    setItens([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return { itens, adicionar, limpar };
}
