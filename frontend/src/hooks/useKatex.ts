import { useEffect, useRef } from 'react';
import katex from 'katex';

interface KatexOptions {
  displayMode?: boolean;
  throwOnError?: boolean;
}

/**
 * Hook para renderizar LaTeX em um elemento DOM via KaTeX.
 * Encapsula o efeito colateral de renderização em refs,
 * facilitando testes (basta mockar katex.render) e reuso.
 */
export function useKatex(latex: string, options: KatexOptions = {}) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!ref.current || !latex) {
      if (ref.current) ref.current.textContent = '';
      return;
    }

    katex.render(latex, ref.current, {
      throwOnError: false,
      displayMode: false,
      ...options,
    });
  }, [latex, options.displayMode]);

  return ref;
}
