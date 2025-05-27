// Add React TypeScript declaration
import * as React from 'react';
import 'react';

declare module 'react-markdown' {
  interface ReactMarkdownProps {
    children: string;
    remarkPlugins?: any[];
    rehypePlugins?: any[];
    components?: any;
  }
  
  const ReactMarkdown: React.FC<ReactMarkdownProps>;
  export default ReactMarkdown;
}

declare module 'remark-gfm' {
  const remarkGfm: any;
  export default remarkGfm;
}

declare module 'rehype-highlight' {
  const rehypeHighlight: any;
  export default rehypeHighlight;
}

// CSS module declarations
declare module '*.css' {
  const content: any;
  export default content;
}

declare module '*.css';