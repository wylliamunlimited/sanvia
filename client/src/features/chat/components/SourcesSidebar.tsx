import React, { useState, useEffect } from 'react';
import { SourceItem } from '../../api/chatApi';

interface SourcesSidebarProps {
  isOpen: boolean;
  sources: SourceItem[];
  onClose: () => void;
  showAllSources?: boolean;
}

interface SourceWithMeta extends SourceItem {
  domain: string;
  faviconUrl: string;
}

const SourcesSidebar: React.FC<SourcesSidebarProps> = ({ 
  isOpen, 
  sources, 
  onClose,
  showAllSources = false
}) => {
  if (!isOpen) return null;

  const [sourcesWithMeta, setSourcesWithMeta] = useState<SourceWithMeta[]>([]);

  // Extract domain from URL
  const getDomain = (url: string) => {
    try {
      const domain = new URL(url).hostname.replace('www.', '');
      return domain;
    } catch {
      return '';
    }
  };

  // Get favicon URL
  const getFaviconUrl = (domain: string) => {
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=64`;
  };

  // Process sources to add metadata
  useEffect(() => {
    if (sources.length) {
      const enhanced = sources.map(source => {
        const domain = getDomain(source.url);
        return {
          ...source,
          domain,
          faviconUrl: getFaviconUrl(domain)
        };
      });
      setSourcesWithMeta(enhanced);
    }
  }, [sources]);

  const handleSourceClick = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="sources-sidebar">
      <div className="sources-header">
        <h3>{showAllSources ? 'Sources' : 'Sources'}</h3>
        <button className="close-sidebar" onClick={onClose}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div className="sources-content">
        {sourcesWithMeta.length === 0 ? (
          <p className="no-sources">No sources available</p>
        ) : (
          <ul className="sources-list">
            {sourcesWithMeta.map((source, index) => (
              <li 
                key={index} 
                className="source-item"
                onClick={() => handleSourceClick(source.url)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSourceClick(source.url);
                  }
                }}
                tabIndex={0}
                role="button"
                aria-label={`View source: ${source.title}`}
              >
                <div className="source-item-content">
                  <div className="source-domain">
                    <img 
                      src={source.faviconUrl} 
                      alt={source.domain}
                      className="source-favicon"
                      onError={(e) => {
                        // If favicon fails to load, hide the image
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                      }}
                    />
                    {source.domain}
                  </div>
                  <div className="source-link">
                    {source.title}
                  </div>
                  {source.content && (
                    <div className="source-meta">
                      <span className="source-preview">{source.content}</span>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default SourcesSidebar; 