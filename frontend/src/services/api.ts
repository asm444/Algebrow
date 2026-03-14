const API_BASE = 'http://localhost:8000/api';

const TIMEOUT_MS = 10_000; // 10 segundos

export interface Passo {
  nivel: number;
  descricao: string;
  regra: string;
  justificativa?: string;
  metodo?: string;
  latex_antes?: string;
  latex_depois?: string;
}

export interface CalcularResponse {
  entrada: string;
  latex_entrada: string;
  latex_resultado: string;
  valor_numerico: string;
  passos: Passo[];
  erro?: string;
}

export async function calcular(
  expressao: string,
  verbosidade: number = 3,
  signal?: AbortSignal
): Promise<CalcularResponse> {
  const timeoutController = new AbortController();
  const timeoutId = setTimeout(() => timeoutController.abort(), TIMEOUT_MS);

  // Combina o signal externo (cancelamento do usuário) com o timeout interno
  const combinedSignal = signal
    ? AbortSignal.any([signal, timeoutController.signal])
    : timeoutController.signal;

  try {
    const res = await fetch(`${API_BASE}/calcular`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expressao, modo: 'simplificar', verbosidade }),
      signal: combinedSignal,
    });

    if (!res.ok) {
      throw new Error(`Erro na API: ${res.status}`);
    }

    return await res.json();
  } catch (e) {
    if (e instanceof DOMException && e.name === 'AbortError') {
      if (signal?.aborted) {
        throw new Error('Requisição cancelada');
      }
      throw new Error('Tempo limite excedido (10s)');
    }
    throw e;
  } finally {
    clearTimeout(timeoutId);
  }
}
