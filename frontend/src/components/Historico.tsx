interface ItemHistorico {
  expressao: string;
  latex_resultado: string;
  timestamp: number;
}

interface Props {
  itens: ItemHistorico[];
  onSelecionar: (expressao: string) => void;
  onLimpar: () => void;
}

export function Historico({ itens, onSelecionar, onLimpar }: Props) {
  if (itens.length === 0) return null;

  return (
    <div className="historico-container">
      <div className="historico-cabecalho">
        <h3>Histórico</h3>
        <button onClick={onLimpar} className="btn-limpar">Limpar</button>
      </div>
      <ul className="historico-lista">
        {itens.map(item => (
          <li key={item.timestamp}>
            <button
              className="historico-item"
              onClick={() => onSelecionar(item.expressao)}
            >
              <span className="historico-expressao">{item.expressao}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
