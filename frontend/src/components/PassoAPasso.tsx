import { useState } from 'react';
import { useKatex } from '../hooks/useKatex';
import type { Passo } from '../services/api';

interface Props {
  passos: Passo[];
}

export function PassoAPasso({ passos }: Props) {
  if (passos.length === 0) return null;

  return (
    <div className="passos-container">
      <h3>Passo a passo</h3>
      <div className="passos-lista">
        {passos.map((passo, i) => (
          <PassoItem
            key={`${passo.regra}-${passo.nivel}-${passo.descricao}`}
            passo={passo}
            numero={i + 1}
          />
        ))}
      </div>
    </div>
  );
}

function PassoItem({ passo, numero }: { passo: Passo; numero: number }) {
  const [expandido, setExpandido] = useState(false);
  const antesRef = useKatex(passo.latex_antes ?? '');
  const depoisRef = useKatex(passo.latex_depois ?? '');

  const temDetalhes = !!(passo.justificativa || passo.metodo);

  return (
    <div className={`passo-item passo-nivel-${passo.nivel}`}>
      <div
        className="passo-cabecalho"
        onClick={() => temDetalhes && setExpandido(!expandido)}
        role={temDetalhes ? 'button' : undefined}
        tabIndex={temDetalhes ? 0 : undefined}
        onKeyDown={e => {
          if (temDetalhes && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            setExpandido(!expandido);
          }
        }}
        style={{ cursor: temDetalhes ? 'pointer' : 'default' }}
      >
        <span className="passo-numero">{numero}</span>
        <span className="passo-descricao">{passo.descricao}</span>
        {temDetalhes && <span className="passo-toggle">{expandido ? '▼' : '▶'}</span>}
      </div>

      {passo.latex_antes && passo.latex_depois && (
        <div className="passo-transformacao">
          <span ref={antesRef} />
          <span className="passo-seta">→</span>
          <span ref={depoisRef} />
        </div>
      )}

      {expandido && temDetalhes && (
        <div className="passo-detalhes">
          {passo.justificativa && (
            <p className="passo-justificativa">
              <strong>Por quê:</strong> {passo.justificativa}
            </p>
          )}
          {passo.metodo && (
            <p className="passo-metodo">
              <strong>Como:</strong> {passo.metodo}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
