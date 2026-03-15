import { useCallback, useEffect, useRef, useState } from 'react';
import { useCalcular } from './hooks/useCalcular';
import { useHistorico } from './hooks/useHistorico';
import { EntradaExpressao } from './components/EntradaExpressao';
import { ResultadoPrincipal } from './components/ResultadoPrincipal';
import { PassoAPasso } from './components/PassoAPasso';
import { Historico } from './components/Historico';
import { Manual } from './components/Manual';
import 'katex/dist/katex.min.css';
import './App.css';

function App() {
  const { resultado, carregando, erro, resolver } = useCalcular();
  const { itens, adicionar, limpar } = useHistorico();
  const ultimoAdicionado = useRef('');
  const [expressaoManual, setExpressaoManual] = useState('');

  // Adiciona ao histórico quando resultado muda
  useEffect(() => {
    if (resultado && resultado.latex_resultado && resultado.entrada !== ultimoAdicionado.current) {
      ultimoAdicionado.current = resultado.entrada;
      adicionar(resultado.entrada, resultado.latex_resultado);
    }
  }, [resultado, adicionar]);

  const handleResolver = useCallback((expressao: string, verbosidade: number) => {
    resolver(expressao, verbosidade);
  }, [resolver]);

  const handleExemploManual = useCallback((expressao: string) => {
    setExpressaoManual(expressao);
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Algebrow</h1>
        <p className="app-subtitulo">Calculadora simbólica com resolução passo a passo</p>
      </header>

      <main className="app-main">
        <Manual onExemplo={handleExemploManual} />
        <EntradaExpressao
          onResolver={handleResolver}
          carregando={carregando}
          expressaoExterna={expressaoManual}
        />
        <ResultadoPrincipal resultado={resultado} erro={erro} />
        {resultado && <PassoAPasso passos={resultado.passos} />}
      </main>

      <aside className="app-aside">
        <Historico
          itens={itens}
          onSelecionar={(expr) => handleResolver(expr, 3)}
          onLimpar={limpar}
        />
      </aside>
    </div>
  );
}

export default App;
