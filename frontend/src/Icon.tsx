export function Icon({ name, size = 18 }: { name: string; size?: number }) {
  const paths: Record<string, string> = {
    grid: 'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
    search: 'M21 21l-5-5 M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0',
    market: 'M4 19V9 M10 19V4 M16 19v-7 M22 19H2',
    users: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8 M22 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75',
    target: 'M22 12a10 10 0 1 1-10-10 M18 12a6 6 0 1 1-6-6 M12 12l9-9 M16 3h5v5',
    route: 'M4 5a2 2 0 1 0 4 0 2 2 0 0 0-4 0 M16 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0 M8 5h9a4 4 0 0 1 0 8H7a3 3 0 0 0 0 6h9',
    deck: 'M3 3h18v13H3z M12 16v5 M8 21h8 M7 12V9 M12 12V6 M17 12v-4',
    file: 'M14 2H4v20h16V8z M14 2v6h6 M8 13h8 M8 17h5',
    chevron: 'M9 5l7 7-7 7', down: 'M6 9l6 6 6-6', plus: 'M12 5v14 M5 12h14',
    close: 'M6 6l12 12 M18 6L6 18', arrow: 'M4 12h16 M14 6l6 6-6 6',
    globe: 'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0 M2 12h20 M12 2a20 20 0 0 1 0 20 20 20 0 0 1 0-20',
    check: 'M5 12l4 4L19 6', info: 'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0 M12 11v6 M12 7h.01',
    filter: 'M4 7h16 M7 12h10 M10 17h4', external: 'M15 3h6v6 M10 14L21 3 M21 14v7H3V3h7',
    book: 'M12 5c-3-3-7-3-10-2v16c3-1 7-1 10 2 3-3 7-3 10-2V3c-3-1-7-1-10 2z M12 5v16',
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d={paths[name] ?? paths.grid} /></svg>;
}
