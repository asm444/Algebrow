import { useState, useRef, useEffect } from 'react';
import katex from 'katex';

interface Props {
  onResolver: (expressao: string, verbosidade: number) => void;
  carregando: boolean;
}

export function EntradaExpressao({ onResolver, carregando }: Props) {
  const [expressao, setExpressao] = useState('');
  const [verbosidade, setVerbosidade] = useState(3);
  const previewRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Preview LaTeX em tempo real (katex.render sanitiza a saída internamente)
  useEffect(() => {
    if (!previewRef.current) return;
    const texto = expressao.trim();
    if (!texto) {
      previewRef.current.textContent = '';
      const placeholder = document.createElement('span');
      placeholder.className = 'placeholder';
      placeholder.textContent = 'Digite uma expressão...';
      previewRef.current.replaceChildren(placeholder);
      return;
    }

    try {
      const latex = textoParaLatexPreview(texto);
      katex.render(latex, previewRef.current, { throwOnError: false, displayMode: true });
    } catch {
      previewRef.current.textContent = texto;
    }
  }, [expressao]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (expressao.trim()) {
      onResolver(expressao.trim(), verbosidade);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="entrada-container">
      <div className="preview-area" ref={previewRef} />

      <div className="input-row">
        <input
          ref={inputRef}
          type="text"
          value={expressao}
          onChange={e => setExpressao(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="sqrt(216), 2^3 + log_3(9), 3/4 + 1/4 ..."
          className="input-expressao"
          autoFocus
        />
        <button type="submit" disabled={carregando || !expressao.trim()} className="btn-resolver">
          {carregando ? '...' : '='}
        </button>
      </div>

      <div className="verbosidade-row">
        <label>Detalhamento:</label>
        <input
          type="range"
          min={0}
          max={4}
          value={verbosidade}
          onChange={e => setVerbosidade(Number(e.target.value))}
        />
        <span className="verbosidade-label">{LABELS_VERBOSIDADE[verbosidade]}</span>
      </div>
    </form>
  );
}

const LABELS_VERBOSIDADE: Record<number, string> = {
  0: 'Só resultado',
  1: 'Passos principais',
  2: 'Intermediário',
  3: 'Detalhado',
  4: 'Tudo',
};

function textoParaLatexPreview(texto: string): string {
  return texto
    .replace(/sqrt_(\d+)\(([^)]+)\)/g, '\\sqrt[$1]{$2}')
    .replace(/sqrt\(([^)]+)\)/g, '\\sqrt{$1}')
    .replace(/log_(\d+)\(([^)]+)\)/g, '\\log_{$1}($2)')
    .replace(/log\(([^)]+)\)/g, '\\log($1)')
    .replace(/(\d+)\^(\d+)/g, '$1^{$2}')
    .replace(/(\d+)\/(\d+)/g, '\\frac{$1}{$2}');
}
