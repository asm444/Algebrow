import { useState, useCallback, useRef } from 'react';
import { calcular } from '../services/api';
import type { CalcularResponse } from '../services/api';

export function useCalcular() {
  const [resultado, setResultado] = useState<CalcularResponse | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState('');
  const abortRef = useRef<AbortController | null>(null);

  const resolver = useCallback(async (expressao: string, verbosidade: number = 3) => {
    if (!expressao.trim()) return;

    // Cancela requisição anterior se ainda estiver em andamento
    if (abortRef.current) {
      abortRef.current.abort();
    }

    const controller = new AbortController();
    abortRef.current = controller;

    setCarregando(true);
    setErro('');

    try {
      const res = await calcular(expressao, verbosidade, controller.signal);
      // Ignora resultado se esta requisição já foi cancelada
      if (controller.signal.aborted) return;

      if (res.erro) {
        setErro(res.erro);
        setResultado(null);
      } else {
        setResultado(res);
      }
    } catch (e) {
      if (controller.signal.aborted) return;

      if (e instanceof TypeError && e.message === 'Failed to fetch') {
        setErro('Não foi possível conectar à API. Verifique se o servidor está rodando.');
      } else {
        setErro(e instanceof Error ? e.message : 'Erro desconhecido');
      }
      setResultado(null);
    } finally {
      if (!controller.signal.aborted) {
        setCarregando(false);
      }
      if (abortRef.current === controller) {
        abortRef.current = null;
      }
    }
  }, []);

  const cancelar = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
      setCarregando(false);
    }
  }, []);

  return { resultado, carregando, erro, resolver, cancelar };
}
