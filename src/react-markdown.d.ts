declare module 'react-markdown' {
  import React from 'react';
  
  export interface ReactMarkdownProps {
    children: string;
    remarkPlugins?: any[];
    rehypePlugins?: any[];
    components?: {
      [key: string]: React.ComponentType<any>;
    };
    className?: string;
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
