import { useKatex } from '../hooks/useKatex';
import type { CalcularResponse } from '../services/api';

interface Props {
  resultado: CalcularResponse | null;
  erro: string;
}

export function ResultadoPrincipal({ resultado, erro }: Props) {
  const latexEntradaRef = useKatex(resultado?.latex_entrada ?? '');
  const latexResultadoRef = useKatex(resultado?.latex_resultado ?? '', { displayMode: true });

  if (erro) {
    return <div className="resultado-erro">{erro}</div>;
  }

  if (!resultado) return null;

  return (
    <div className="resultado-container">
      <div className="resultado-expressao">
        <span ref={latexEntradaRef} /> <span className="resultado-igual">=</span>
      </div>
      <div className="resultado-principal" ref={latexResultadoRef} />
      {resultado.valor_numerico && (
        <div className="resultado-numerico">
          ≈ {resultado.valor_numerico}
        </div>
      )}
    </div>
  );
}
