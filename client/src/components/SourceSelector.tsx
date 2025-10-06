import { useState } from 'react';
import clsx from 'clsx';

export default function SourceSelector({ onChange }: { onChange: (src: string) => void }) {
  const [active, setActive] = useState('both');
  const options = ['amazon', 'flipkart', 'both'];

  return (
    <div className="flex gap-2 justify-center mt-3">
      {options.map((o) => (
        <button
          key={o}
          onClick={() => {
            setActive(o);
            onChange(o);
          }}
          className={clsx(
            'px-3 py-1.5 rounded-full border transition',
            active === o
              ? 'bg-brand-600 text-white border-brand-600 shadow'
              : 'bg-white/70 dark:bg-slate-800/60 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:bg-white/90 dark:hover:bg-slate-700/70'
          )}
        >
          {o[0].toUpperCase() + o.slice(1)}
        </button>
      ))}
    </div>
  );
}
