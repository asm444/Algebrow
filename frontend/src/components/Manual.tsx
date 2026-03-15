import { useState, useRef, useEffect, useCallback } from 'react';
import katex from 'katex';

interface CategoriaManual {
  titulo: string;
  descricao: string;
  exemplos: { latex: string; entrada: string; descricao: string }[];
}

const CATEGORIAS: CategoriaManual[] = [
  {
    titulo: 'Aritmética',
    descricao: 'Operações fundamentais com números inteiros, frações e decimais.',
    exemplos: [
      { latex: '3 + 4', entrada: '3 + 4', descricao: 'Soma' },
      { latex: '10 - 3', entrada: '10 - 3', descricao: 'Subtração' },
      { latex: '6 \\times 7', entrada: '6 \\times 7', descricao: 'Multiplicação' },
      { latex: '\\frac{15}{4}', entrada: '\\frac{15}{4}', descricao: 'Divisão / Fração' },
      { latex: '\\frac{3}{4} + \\frac{1}{6}', entrada: '\\frac{3}{4} + \\frac{1}{6}', descricao: 'Soma de frações' },
      { latex: '\\frac{2}{3} \\cdot \\frac{5}{7}', entrada: '\\frac{2}{3} \\cdot \\frac{5}{7}', descricao: 'Multiplicação de frações' },
      { latex: '-5 + 3', entrada: '-5 + 3', descricao: 'Números negativos' },
      { latex: '(2 + 3) \\times 4', entrada: '(2 + 3) \\times 4', descricao: 'Parênteses' },
    ],
  },
  {
    titulo: 'Potências',
    descricao: 'Exponenciação com simplificação automática.',
    exemplos: [
      { latex: '2^{10}', entrada: '2^{10}', descricao: '2 elevado a 10' },
      { latex: '3^{4}', entrada: '3^{4}', descricao: '3 elevado a 4' },
      { latex: '5^{3}', entrada: '5^{3}', descricao: '5 elevado a 3' },
      { latex: '2^{3} + 3^{2}', entrada: '2^{3} + 3^{2}', descricao: 'Soma de potências' },
    ],
  },
  {
    titulo: 'Raízes',
    descricao: 'Radiciação com simplificação automática (extrai fatores do radical).',
    exemplos: [
      { latex: '\\sqrt{216}', entrada: '\\sqrt{216}', descricao: 'Raiz quadrada de 216' },
      { latex: '\\sqrt{50}', entrada: '\\sqrt{50}', descricao: 'Raiz quadrada de 50 → 5√2' },
      { latex: '\\sqrt{144}', entrada: '\\sqrt{144}', descricao: 'Raiz quadrada exata' },
      { latex: '\\sqrt[3]{8}', entrada: '\\sqrt[3]{8}', descricao: 'Raiz cúbica de 8' },
      { latex: '\\sqrt[3]{27}', entrada: '\\sqrt[3]{27}', descricao: 'Raiz cúbica de 27' },
      { latex: '\\sqrt[4]{81}', entrada: '\\sqrt[4]{81}', descricao: 'Raiz quarta de 81' },
    ],
  },
  {
    titulo: 'Logaritmos',
    descricao: 'Logaritmos em qualquer base.',
    exemplos: [
      { latex: '\\log_{2}{8}', entrada: '\\log_{2}{8}', descricao: 'log base 2 de 8' },
      { latex: '\\log_{3}{9}', entrada: '\\log_{3}{9}', descricao: 'log base 3 de 9' },
      { latex: '\\log_{10}{1000}', entrada: '\\log_{10}{1000}', descricao: 'log base 10 de 1000' },
      { latex: '\\log_{5}{125}', entrada: '\\log_{5}{125}', descricao: 'log base 5 de 125' },
    ],
  },
  {
    titulo: 'Expressões Mistas',
    descricao: 'Combine frações, raízes, potências e logaritmos.',
    exemplos: [
      { latex: '\\frac{3}{4} + \\sqrt{2}', entrada: '\\frac{3}{4} + \\sqrt{2}', descricao: 'Fração + raiz' },
      { latex: '2^{3} + \\log_{2}{16}', entrada: '2^{3} + \\log_{2}{16}', descricao: 'Potência + logaritmo' },
      { latex: '\\sqrt{3} \\cdot \\sqrt{12}', entrada: '\\sqrt{3} \\cdot \\sqrt{12}', descricao: 'Produto de raízes' },
      { latex: '\\frac{1}{2} + \\frac{1}{3} + \\frac{1}{6}', entrada: '\\frac{1}{2} + \\frac{1}{3} + \\frac{1}{6}', descricao: 'Soma de várias frações' },
    ],
  },
  {
    titulo: 'Equações',
    descricao: 'Equações de 1o e 2o grau com resolução passo a passo.',
    exemplos: [
      { latex: '2x + 3 = 7', entrada: '2x + 3 = 7', descricao: 'Equação de 1o grau' },
      { latex: 'x^{2} - 5x + 6 = 0', entrada: 'x^{2} - 5x + 6 = 0', descricao: 'Equação de 2o grau (Bhaskara)' },
      { latex: '3x - 1 = x + 5', entrada: '3x - 1 = x + 5', descricao: 'Variável nos dois lados' },
      { latex: 'x^{2} - 4 = 0', entrada: 'x^{2} - 4 = 0', descricao: 'Diferença de quadrados' },
    ],
  },
  {
    titulo: 'Inequações',
    descricao: 'Inequações com >, <, ≥, ≤.',
    exemplos: [
      { latex: '2x + 1 > 5', entrada: '2x + 1 > 5', descricao: 'Maior que' },
      { latex: '3x - 2 < 10', entrada: '3x - 2 < 10', descricao: 'Menor que' },
      { latex: 'x + 4 \\geq 7', entrada: 'x + 4 \\geq 7', descricao: 'Maior ou igual (\\geq)' },
      { latex: '5x \\leq 20', entrada: '5x \\leq 20', descricao: 'Menor ou igual (\\leq)' },
    ],
  },
];

function LatexPreview({ latex }: { latex: string }) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    try {
      katex.render(latex, ref.current, { throwOnError: false });
    } catch {
      if (ref.current) ref.current.textContent = latex;
    }
  }, [latex]);

  return <span ref={ref} />;
}

interface ManualProps {
  onExemplo: (expressao: string) => void;
}

export function Manual({ onExemplo }: ManualProps) {
  const [aberto, setAberto] = useState(false);
  const [categoriaAtiva, setCategoriaAtiva] = useState(0);

  const handleClickExemplo = useCallback(
    (entrada: string) => {
      onExemplo(entrada);
      setAberto(false);
    },
    [onExemplo],
  );

  return (
    <div className="manual-container">
      <button
        type="button"
        className="btn-manual"
        onClick={() => setAberto(!aberto)}
        aria-expanded={aberto}
      >
        {aberto ? 'Fechar Manual' : 'Como escrever? (Manual LaTeX)'}
      </button>

      {aberto && (
        <div className="manual-painel">
          <div className="manual-cabecalho">
            <h2>Manual — Escrita em LaTeX</h2>
            <p>
              Digite expressões em <strong>LaTeX puro</strong>. O sistema interpreta e calcula
              automaticamente. Clique em qualquer exemplo para usá-lo.
            </p>
          </div>

          <div className="manual-sintaxe">
            <h3>Referência Rápida</h3>
            <table className="manual-tabela">
              <thead>
                <tr>
                  <th>Operação</th>
                  <th>LaTeX</th>
                  <th>Resultado</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Fração</td>
                  <td><code>\frac{'{a}'}{'{b}'}</code></td>
                  <td><LatexPreview latex="\\frac{a}{b}" /></td>
                </tr>
                <tr>
                  <td>Raiz quadrada</td>
                  <td><code>\sqrt{'{x}'}</code></td>
                  <td><LatexPreview latex="\\sqrt{x}" /></td>
                </tr>
                <tr>
                  <td>Raiz n-ésima</td>
                  <td><code>\sqrt[n]{'{x}'}</code></td>
                  <td><LatexPreview latex="\\sqrt[3]{x}" /></td>
                </tr>
                <tr>
                  <td>Potência</td>
                  <td><code>a^{'{b}'}</code></td>
                  <td><LatexPreview latex="a^{b}" /></td>
                </tr>
                <tr>
                  <td>Logaritmo</td>
                  <td><code>\log_{'{'}<em>b</em>{'}'}{'{x}'}</code></td>
                  <td><LatexPreview latex="\\log_{b}{x}" /></td>
                </tr>
                <tr>
                  <td>Multiplicação</td>
                  <td><code>\cdot</code> ou <code>\times</code></td>
                  <td><LatexPreview latex="a \\cdot b" /></td>
                </tr>
                <tr>
                  <td>Maior/igual</td>
                  <td><code>\geq</code></td>
                  <td><LatexPreview latex="x \\geq 5" /></td>
                </tr>
                <tr>
                  <td>Menor/igual</td>
                  <td><code>\leq</code></td>
                  <td><LatexPreview latex="x \\leq 10" /></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="manual-dica">
            <strong>Dica:</strong> Você também pode usar a sintaxe simplificada:
            {' '}<code>sqrt(216)</code>, <code>2^3</code>, <code>log_2(8)</code>, <code>3/4</code>.
            O sistema aceita ambas as formas.
          </div>

          <div className="manual-categorias">
            <nav className="manual-nav">
              {CATEGORIAS.map((cat, i) => (
                <button
                  key={cat.titulo}
                  type="button"
                  className={`manual-nav-btn ${i === categoriaAtiva ? 'ativo' : ''}`}
                  onClick={() => setCategoriaAtiva(i)}
                >
                  {cat.titulo}
                </button>
              ))}
            </nav>

            <div className="manual-conteudo">
              <p className="manual-cat-descricao">{CATEGORIAS[categoriaAtiva].descricao}</p>
              <div className="manual-exemplos">
                {CATEGORIAS[categoriaAtiva].exemplos.map((ex) => (
                  <button
                    key={ex.entrada}
                    type="button"
                    className="manual-exemplo"
                    onClick={() => handleClickExemplo(ex.entrada)}
                    title={`Usar: ${ex.entrada}`}
                  >
                    <div className="exemplo-codigo">
                      <code>{ex.entrada}</code>
                    </div>
                    <div className="exemplo-preview">
                      <LatexPreview latex={ex.latex} />
                    </div>
                    <div className="exemplo-descricao">{ex.descricao}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
