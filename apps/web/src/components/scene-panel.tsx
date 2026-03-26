type ScenePanelProps = {
  title: string;
  items: string[];
};

export function ScenePanel({ title, items }: ScenePanelProps) {
  return (
    <section className="glass p-6">
      <h2 className="text-xl font-semibold text-ink">{title}</h2>
      <ul className="mt-4 space-y-3 text-sm text-slate-700">
        {items.map((item) => (
          <li
            key={item}
            className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-3"
          >
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}

