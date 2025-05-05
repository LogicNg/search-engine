// hooks/useQueryHistory.ts
import { useState, useEffect } from 'react';

const LOCAL_STORAGE_KEY = 'searchQueryHistory';

export const useQueryHistory = () => {
  const [queryHistory, setQueryHistory] = useState<string[]>(() => {
    if (typeof window === 'undefined') return [];
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(queryHistory));
  }, [queryHistory]);

  const addQueryHistory = (query: string) => {
    if (!query.trim()) return;

    setQueryHistory(prev => [query, ...prev]);
    console.log('Added query to history:', query);
  };

  const clearQueryHistory = () => {
    setQueryHistory([]);
  };

  const deleteQueryHistory = (query: string) => {
    setQueryHistory(prev => prev.filter(q => q !== query));
  }

  return { queryHistory, addQueryHistory, deleteQueryHistory, clearQueryHistory };
};